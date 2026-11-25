"""Prepare PiSSA residual weights and initial adapters for native MLX-LM."""

from copy import deepcopy
from math import isfinite

import mlx.core as mx
import numpy as np
from mlx import nn
from mlx_lm.utils import quantize_model

_AFFINE_4BIT = {"bits": 4, "group_size": 64, "mode": "affine"}
_QUANTIZATION_FIELDS = ("quantization", "quantization_config")
_QUANTIZED_MODULES = (nn.QuantizedLinear, nn.QuantizedEmbedding)


def _target_linears(
    model: nn.Module, keys: list[str], num_layers: int, optional_keys: set[str]
) -> dict[str, nn.Linear]:
    layers = getattr(model, "layers", ())
    if type(num_layers) is not int or (num_layers != -1 and not 1 <= num_layers <= len(layers)):
        raise ValueError("num_layers must be -1 or select a positive number of model blocks.")
    if not layers:
        raise ValueError("PiSSA requires a model with decoder blocks.")

    model_modules = model.named_modules()
    if any(isinstance(module, _QUANTIZED_MODULES) for _, module in model_modules):
        raise ValueError("PiSSA requires the original non-quantized weights.")
    paths = {id(module): path for path, module in model_modules}

    targets = {}
    found = set()
    selected_layers = layers if num_layers == -1 else layers[-num_layers:]
    for block in selected_layers:
        modules = dict(block.named_modules())
        for key in keys:
            path = f"{paths[id(block)]}.{key}"
            if key not in modules:
                if key in optional_keys:
                    continue
                raise ValueError(f"{path}: PiSSA target is missing.")
            module = modules[key]
            if not isinstance(module, nn.Linear):
                raise TypeError(f"{path}: PiSSA target must be a dense linear projection.")
            targets[path] = module
            found.add(key)
    unmatched = set(keys) - found
    if unmatched:
        raise ValueError(f"PiSSA targets absent from all selected blocks: {sorted(unmatched)}.")
    return targets


def _factors(weight: mx.array, rank: int, scale: float, path: str) -> tuple[mx.array, mx.array]:
    try:
        u, singular_values, vt = np.linalg.svd(np.asarray(weight), full_matrices=False)
    except np.linalg.LinAlgError as exc:
        raise ValueError(f"{path}: SVD failed for the source projection.") from exc

    root = np.sqrt(singular_values[:rank] / scale)
    if not np.isfinite(root).all():
        raise ValueError(f"{path}: SVD produced non-finite adapter factors.")
    # Native MLX stores A[in, rank] and B[rank, out].
    a = mx.array(vt[:rank].T * root)
    b = mx.array(root[:, None] * u[:, :rank].T)
    return a, b


def _remove_principal_components(
    linear: nn.Linear, rank: int, scale: float, path: str
) -> tuple[mx.array, mx.array]:
    source = linear.weight.astype(mx.float32)
    a, b = _factors(source, rank, scale, path)
    delta = (scale * b.T) @ a.T
    linear.weight = (source - delta).astype(linear.weight.dtype)
    mx.eval(linear.weight, a, b)
    return a, b


def _dora_magnitude(
    residual: nn.Module, a: mx.array, b: mx.array, scale: float, path: str
) -> mx.array:
    weight = residual.weight
    if isinstance(residual, nn.QuantizedLinear):
        weight = mx.dequantize(
            weight,
            residual.scales,
            residual.biases,
            group_size=residual.group_size,
            bits=residual.bits,
            mode=residual.mode,
        )
    # Normalize against the effective weight that DoRALinear uses at initialization.
    magnitude = mx.linalg.norm(weight + (scale * b.T) @ a.T, axis=1)
    if not mx.all(mx.isfinite(magnitude) & (magnitude > 0)).item():
        raise ValueError(f"{path}: DoRA requires finite, nonzero reconstructed row norms.")
    return magnitude


def prepare_model(
    model: nn.Module, model_config: dict, preset: dict
) -> tuple[nn.Module, dict, dict[str, mx.array]]:
    """Replace dense projections in place and return a stock base and flat adapter tensors.

    The input model supplies the original dense source weights. The adapter is tied to
    the resulting residual model. Output reconstruction applies with dropout disabled,
    up to rounding from storing or quantizing the residual.
    """
    if any(model_config.get(field) is not None for field in _QUANTIZATION_FIELDS):
        raise ValueError("PiSSA requires the original non-quantized weights.")
    fine_tune_type = preset.get("fine_tune_type")
    if fine_tune_type not in ("lora", "dora"):
        raise ValueError("PiSSA requires fine_tune_type: lora or dora.")
    quantization = preset.get("pissa_quantization")
    if quantization is not None and quantization != _AFFINE_4BIT:
        raise ValueError("PiSSA supports only affine 4-bit quantization with group_size 64.")

    parameters = preset.get("lora_parameters")
    if not isinstance(parameters, dict):
        raise TypeError("PiSSA requires a lora_parameters mapping.")
    rank, scale, keys = (parameters.get(key) for key in ("rank", "scale", "keys"))
    if type(rank) is not int or rank <= 0:
        raise ValueError("PiSSA rank must be a positive integer.")
    if type(scale) not in (int, float) or not isfinite(scale) or scale <= 0:
        raise ValueError("PiSSA scale must be finite and positive.")
    if (
        not isinstance(keys, list)
        or not keys
        or any(not isinstance(key, str) or not key for key in keys)
    ):
        raise ValueError("PiSSA requires explicit projection names in lora_parameters.keys.")
    if len(keys) != len(set(keys)):
        raise ValueError("PiSSA projection names must be unique.")

    optional_keys = preset.get("pissa_optional_keys", [])
    if not isinstance(optional_keys, list) or any(
        not isinstance(key, str) or key not in keys for key in optional_keys
    ):
        raise ValueError("pissa_optional_keys must be a list of declared projection names.")

    targets = _target_linears(model, keys, preset.get("num_layers"), set(optional_keys))
    for path, linear in targets.items():
        weight = linear.weight
        if weight.ndim != 2 or weight.dtype not in (mx.bfloat16, mx.float16, mx.float32):
            raise ValueError(f"{path}: expected a matrix of BF16, FP16, or FP32 weights.")
        if rank > min(weight.shape):
            raise ValueError(f"{path}: rank {rank} exceeds the weight dimensions {weight.shape}.")
        if quantization is not None and weight.shape[1] % _AFFINE_4BIT["group_size"]:
            raise ValueError(
                f"{path}: input dimension must be divisible by the quantization group."
            )
    del weight

    adapter = {}
    for path, linear in targets.items():
        a, b = _remove_principal_components(linear, rank, scale, path)
        adapter[f"{path}.lora_a"] = a
        adapter[f"{path}.lora_b"] = b
    target_paths = tuple(targets)
    del targets, linear

    residual_config = deepcopy(model_config)
    for field in _QUANTIZATION_FIELDS:
        residual_config.pop(field, None)
    if quantization is not None:
        model, residual_config = quantize_model(model, residual_config, **_AFFINE_4BIT)

    residual_modules = dict(model.named_modules())
    if quantization is not None:
        # Materialize one module at a time so the lazy graph releases its dense inputs.
        quantized_linears = set()
        for path, module in residual_modules.items():
            if isinstance(module, _QUANTIZED_MODULES):
                mx.eval(module.parameters())
            if isinstance(module, nn.QuantizedLinear):
                quantized_linears.add(path)
        skipped = set(target_paths) - quantized_linears
        if skipped:
            raise ValueError(f"The quantization recipe skipped PiSSA targets: {sorted(skipped)}.")
    if fine_tune_type == "dora":
        for path in target_paths:
            adapter[f"{path}.m"] = _dora_magnitude(
                residual_modules[path],
                adapter[f"{path}.lora_a"],
                adapter[f"{path}.lora_b"],
                scale,
                path,
            )

    return model, residual_config, adapter
