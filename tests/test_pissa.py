"""PiSSA initialization against tiny Qwen fixtures and stock MLX LM adapters."""

import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import mlx.core as mx
import pytest
import yaml
from jinja2 import Environment
from mlx import nn
from mlx_lm.models.gemma4 import Model as Gemma4Model
from mlx_lm.models.gemma4 import ModelArgs as Gemma4Args
from mlx_lm.models.qwen2 import Model, ModelArgs
from mlx_lm.models.qwen3 import Model as Qwen3Model
from mlx_lm.models.qwen3 import ModelArgs as Qwen3Args
from mlx_lm.tuner.dora import DoRALinear
from mlx_lm.tuner.lora import LoRALinear
from mlx_lm.tuner.utils import load_adapters

from soc_triage.chat_template import NON_THINKING_PREFIX, disable_chat_thinking
from soc_triage.pissa import prepare_model

QUANTIZATION = {"bits": 4, "group_size": 64, "mode": "affine"}
TARGETS = ("self_attn.q_proj", "self_attn.v_proj")
TARGET_PREFIX = "model.layers.1."


@pytest.fixture(params=["qwen2", "qwen3"])
def tiny_qwen(request):
    mx.random.seed(42)
    shared = {
        "model_type": request.param,
        "hidden_size": 64,
        "num_hidden_layers": 2,
        "intermediate_size": 128,
        "num_attention_heads": 4,
        "num_key_value_heads": 2,
        "rms_norm_eps": 1e-6,
        "vocab_size": 96,
        "tie_word_embeddings": False,
    }
    if request.param == "qwen3":
        arguments = Qwen3Args(**shared, max_position_embeddings=256, head_dim=16, rope_theta=1e6)
        model = Qwen3Model(arguments)
    else:
        arguments = ModelArgs(**shared)
        model = Model(arguments)
    model.set_dtype(mx.bfloat16)
    model.eval()
    mx.eval(model.parameters())
    return model, asdict(arguments)


def make_preset(fine_tune_type, quantization=None):
    preset = {
        "fine_tune_type": fine_tune_type,
        "num_layers": 1,
        "lora_parameters": {
            "rank": 8,
            "scale": 1.75,
            "dropout": 0.05,
            "keys": list(TARGETS),
        },
    }
    if quantization is not None:
        preset["pissa_quantization"] = dict(quantization)
    return preset


def dense_weight(module):
    if isinstance(module, nn.QuantizedLinear):
        return mx.dequantize(
            module.weight,
            module.scales,
            module.biases,
            group_size=module.group_size,
            bits=module.bits,
            mode=module.mode,
        ).astype(mx.float32)
    return module.weight.astype(mx.float32)


def relative_error(actual, reference):
    actual = actual.astype(mx.float32)
    reference = reference.astype(mx.float32)
    return (mx.linalg.norm(actual - reference) / mx.linalg.norm(reference)).item()


@pytest.mark.parametrize("quantized", [False, True], ids=["bf16", "4bit"])
@pytest.mark.parametrize("fine_tune_type", ["lora", "dora"])
def test_pissa_reconstructs_through_stock_mlx_adapter(
    tiny_qwen, tmp_path, quantized, fine_tune_type
):
    model, config = tiny_qwen
    before = dict(model.named_modules())
    original = {
        name: (before[name].weight, getattr(before[name], "bias", None))
        for name in (f"{TARGET_PREFIX}{key}" for key in TARGETS)
    }
    # A compatible non-target projection in an earlier block detects scope mistakes.
    untouched_path = "model.layers.0.self_attn.q_proj"
    untouched_weight = before[untouched_path].weight
    tokens = mx.array([[1, 17, 27, 9, 2]])
    original_logits = model(tokens)
    mx.eval(original_logits)

    preset = make_preset(fine_tune_type, QUANTIZATION if quantized else None)
    residual, residual_config, adapter_weights = prepare_model(model, config, preset)

    suffixes = ("lora_a", "lora_b", "m") if fine_tune_type == "dora" else ("lora_a", "lora_b")
    assert set(adapter_weights) == {f"{name}.{suffix}" for name in original for suffix in suffixes}
    assert all(weight.dtype == mx.float32 for weight in adapter_weights.values())
    assert "quantization" not in config
    if quantized:
        assert residual_config["quantization"] == QUANTIZATION
    else:
        assert residual_config == config

    base_modules = dict(residual.named_modules())
    expected_base = nn.QuantizedLinear if quantized else nn.Linear
    assert isinstance(base_modules[untouched_path], expected_base)
    if not quantized:
        assert mx.array_equal(base_modules[untouched_path].weight, untouched_weight).item()
    for name, (weight, bias) in original.items():
        stored = base_modules[name]
        assert isinstance(stored, expected_base)
        if bias is not None:
            assert mx.array_equal(stored.bias, bias).item()
        else:
            assert "bias" not in stored
        # A no-op implementation would keep the original weight here.
        assert relative_error(dense_weight(stored), weight) > 0.25
        if not quantized:
            assert stored.weight.dtype == mx.bfloat16

    config_path = tmp_path / "adapter_config.json"
    config_path.write_text(json.dumps(preset), encoding="utf-8")
    mx.save_safetensors(str(tmp_path / "adapters.safetensors"), adapter_weights)
    restored = load_adapters(residual, str(tmp_path))
    restored.eval()

    expected_adapter = DoRALinear if fine_tune_type == "dora" else LoRALinear
    restored_modules = dict(restored.named_modules())
    installed = {
        name for name, module in restored_modules.items() if isinstance(module, expected_adapter)
    }
    assert installed == set(original)
    for name, (weight, bias) in original.items():
        module = restored_modules[name]
        fused = module.fuse(dequantize=True)
        assert relative_error(fused.weight, weight) < (0.16 if quantized else 0.012)
        if bias is not None:
            assert mx.array_equal(fused.bias, bias).item()
        else:
            assert "bias" not in fused

        if fine_tune_type == "dora":
            adapted = dense_weight(module.linear)
            adapted = adapted + (module.scale * module.lora_b.T) @ module.lora_a.T
            norm = mx.linalg.norm(adapted, axis=1)
            assert mx.allclose(module.m, norm, rtol=1e-5, atol=1e-6).item()

    assert relative_error(restored(tokens), original_logits) < (0.25 if quantized else 0.025)


def test_pissa_rejects_rank_exceeding_target_dimensions(tiny_qwen):
    model, config = tiny_qwen
    preset = make_preset("lora")
    preset["lora_parameters"]["rank"] = 65
    with pytest.raises(ValueError):
        prepare_model(model, config, preset)


def test_pissa_rejects_unsupported_quantization(tiny_qwen):
    model, config = tiny_qwen
    preset = make_preset("lora", {**QUANTIZATION, "bits": 8})
    with pytest.raises(ValueError):
        prepare_model(model, config, preset)


def test_pissa_rejects_already_quantized_base(tiny_qwen):
    model, config = tiny_qwen
    nn.quantize(model, **QUANTIZATION)
    with pytest.raises(ValueError):
        prepare_model(model, {**config, "quantization": QUANTIZATION}, make_preset("lora"))


def test_chat_template_forces_non_thinking_without_repeating_the_prefix():
    tokenizer = SimpleNamespace(
        chat_template="{% if enable_thinking %}thinking{% else %}json{% endif %}"
    )
    disable_chat_thinking(tokenizer)
    disable_chat_thinking(tokenizer)

    assert tokenizer.chat_template.count(NON_THINKING_PREFIX) == 1
    assert Environment().from_string(tokenizer.chat_template).render(enable_thinking=True) == "json"


GEMMA_PRESETS = sorted((Path(__file__).parents[1] / "configs" / "mlx").glob("run[1-5]*.yaml"))


@pytest.mark.parametrize("preset_path", GEMMA_PRESETS, ids=lambda path: path.stem)
def test_gemma4_pissa_targets_match_native_tuner_with_shared_kv(preset_path, tmp_path):
    args = Gemma4Args(
        model_type="gemma4",
        text_config={
            "model_type": "gemma4_text",
            "hidden_size": 64,
            "num_hidden_layers": 4,
            "intermediate_size": 128,
            "num_attention_heads": 4,
            "num_key_value_heads": 2,
            "head_dim": 32,
            "global_head_dim": 32,
            "vocab_size": 96,
            "vocab_size_per_layer_input": 96,
            "num_kv_shared_layers": 2,
            "hidden_size_per_layer_input": 64,
            "layer_types": ["sliding_attention", "full_attention"] * 2,
        },
    )
    model = Gemma4Model(args)
    model.set_dtype(mx.bfloat16)
    preset = yaml.safe_load(preset_path.read_text(encoding="utf-8"))
    residual, _, weights = prepare_model(model, asdict(args), preset)

    targets = {name.removesuffix(".lora_a") for name in weights if name.endswith(".lora_a")}
    assert len(targets) == (6 if preset_path.stem.startswith("run1_") else 24)
    assert all("per_layer_" not in name for name in targets)
    assert all(
        f"layers.{index}.self_attn.v_proj" not in name for index in (2, 3) for name in targets
    )

    (tmp_path / "adapter_config.json").write_text(json.dumps(preset), encoding="utf-8")
    mx.save_safetensors(str(tmp_path / "adapters.safetensors"), weights)
    restored = load_adapters(residual, str(tmp_path))
    restored.eval()
    installed = {
        name
        for name, module in restored.named_modules()
        if isinstance(module, (LoRALinear, DoRALinear))
    }
    assert installed == targets
    assert mx.all(mx.isfinite(restored(mx.array([[1, 17, 27, 9, 2]])))).item()
