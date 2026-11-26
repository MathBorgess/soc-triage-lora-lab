"""Prepare ou confira o par local de pesos residuais e adaptador inicial PiSSA."""

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import mlx.core as mx
import yaml
from mlx_lm.utils import load_model, load_tokenizer, save_config, save_model

from soc_triage.chat_template import NON_THINKING_PREFIX, disable_chat_thinking

PREPARATION_KEYS = (
    "init_lora_weights",
    "pissa_source_model",
    "pissa_quantization",
    "fine_tune_type",
    "num_layers",
)
SOURCE_KEYS = (
    "pissa_source_revision",
    "pissa_source_model_type",
    "disable_thinking",
    "pissa_optional_keys",
)


def preparation_signature(preset: dict) -> str:
    parameters = preset["lora_parameters"]
    signature = {key: preset.get(key) for key in PREPARATION_KEYS}
    signature.update({key: preset[key] for key in SOURCE_KEYS if key in preset})
    signature["lora_parameters"] = {key: parameters[key] for key in ("rank", "scale", "keys")}
    return hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()


def check_prepared(root: Path, signature: str, *, disable_thinking: bool = False) -> None:
    metadata = json.loads((root / "pissa.json").read_text())
    if metadata.get("preset_signature") != signature:
        raise ValueError("O par PiSSA foi preparado para outra configuração.")
    checkpoint = root / "base"
    index = json.loads((checkpoint / "model.safetensors.index.json").read_text())
    shards = set(index["weight_map"].values())
    required = [checkpoint / "config.json", root / "init.safetensors"]
    required.extend(checkpoint / shard for shard in shards)
    if not shards or any(not path.is_file() or path.stat().st_size == 0 for path in required):
        raise ValueError("O par PiSSA está incompleto. Confira a base residual e o adaptador.")
    if disable_thinking:
        tokenizer = load_tokenizer(checkpoint, {"trust_remote_code": False})
        if not (tokenizer.chat_template or "").startswith(NON_THINKING_PREFIX):
            raise ValueError("O tokenizer do par PiSSA está sem o template non-thinking.")


def prepare(preset: dict, source: Path, revision: str, root: Path, signature: str) -> None:
    from soc_triage.pissa import prepare_model

    if not (source / "config.json").is_file():
        raise ValueError("--base precisa apontar para um checkpoint original local.")
    if root.exists():
        raise FileExistsError(f"Use um novo diretório de saída. Já existe: {root}")

    required_revision = preset.get("pissa_source_revision")
    if required_revision and revision != required_revision:
        raise ValueError(f"A revisão exigida pelo preset é {required_revision}.")
    if required_revision and source.parent.name == "snapshots" and source.name != required_revision:
        raise ValueError("A pasta do snapshot diverge da revisão exigida pelo preset.")
    required_model_type = preset.get("pissa_source_model_type")
    config = json.loads((source / "config.json").read_text(encoding="utf-8"))
    if required_model_type and config.get("model_type") != required_model_type:
        raise ValueError(f"A origem precisa ter model_type={required_model_type}.")

    disable_thinking = preset.get("disable_thinking", False)
    tokenizer = load_tokenizer(source, {"trust_remote_code": False})
    if disable_thinking:
        disable_chat_thinking(tokenizer)
    model, config = load_model(source, lazy=True, trust_remote_code=False)
    model, config, weights = prepare_model(model, config, preset)

    root.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=root.parent, prefix=".prepare-pissa-") as staged:
        temporary = Path(staged)
        checkpoint = temporary / "base"
        save_model(checkpoint, model, donate_model=True)
        save_config(config, checkpoint / "config.json")
        tokenizer.save_pretrained(checkpoint)
        mx.save_safetensors(str(temporary / "init.safetensors"), weights)
        metadata = {
            "preset_signature": signature,
            "source_model": preset["pissa_source_model"],
            "source_local_path": str(source.resolve()),
            "source_revision": revision,
        }
        (temporary / "pissa.json").write_text(json.dumps(metadata, indent=2) + "\n")
        check_prepared(temporary, signature, disable_thinking=disable_thinking)
        temporary.rename(root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Preset YAML do laboratório.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--base", type=Path, help="Diretório local dos pesos originais não quantizados."
    )
    mode.add_argument(
        "--check", action="store_true", help="Confira o par local sem carregar pesos."
    )
    mode.add_argument("--serve-model", type=Path, help="Confira a base do adaptador em serviço.")
    parser.add_argument("--revision", help="Revisão de origem do checkpoint local.")
    args = parser.parse_args()
    if args.base is not None and not args.revision:
        parser.error("--base requer --revision para registrar a origem dos pesos.")

    try:
        preset = yaml.safe_load(args.config.read_text())
        if not isinstance(preset, dict):
            raise TypeError("Esperado um mapa de configuração.")
        if args.serve_model is not None and preset.get("init_lora_weights") != "pissa":
            return
        if preset.get("init_lora_weights") != "pissa":
            raise ValueError("O preset precisa definir init_lora_weights: pissa.")
        checkpoint = Path(preset["model"])
        adapter = Path(preset["resume_adapter_file"])
        root = checkpoint.parent
        if checkpoint.name != "base" or adapter != root / "init.safetensors":
            raise ValueError("O preset deve usar base/ e init.safetensors no mesmo diretório.")
        signature = preparation_signature(preset)
        if args.serve_model is not None and args.serve_model.resolve() != checkpoint.resolve():
            raise ValueError(f"Sirva o adaptador PiSSA com a base residual {checkpoint}.")
        if args.check or args.serve_model is not None:
            check_prepared(root, signature, disable_thinking=preset.get("disable_thinking", False))
        else:
            prepare(preset, args.base.expanduser(), args.revision, root, signature)
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        parser.error(f"{error}. Confira o preset e a preparação local do PiSSA.")

    print(f"Par PiSSA verificado em {root}")


if __name__ == "__main__":
    main()
