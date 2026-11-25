"""Treine um preset com o MLX LM no mesmo processo e registre a rodada em runs/<run-id>/.

Equivale a `mlx_lm.lora --config <preset>`, com um callback que grava as losses, os tokens/s e o
pico de memória reportados pelo treinador. As opções de linha de comando sobrescrevem o preset
como no `mlx_lm.lora` (use para o treino curto de verificação). O adaptador e o diretório da
rodada precisam ser novos. Exige o par PiSSA preparado (`make prepare-pissa`).

    uv run --locked python scripts/08_train.py --config configs/mlx/run2_qlora_all_linear.yaml \
        --run-id run2-v12-s42
"""

import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

import mlx.core as mx
import numpy as np
import yaml
from mlx_lm import load
from mlx_lm.lora import CONFIG_DEFAULTS, evaluate_model, train_model, yaml_loader
from mlx_lm.tuner.callbacks import TrainingCallback
from mlx_lm.tuner.datasets import load_dataset
from mlx_lm.utils import load_tokenizer

from soc_triage.chat_template import NON_THINKING_PREFIX
from soc_triage.runlog import environment, sha256

OVERRIDES = {
    "--iters": int,
    "--steps-per-report": int,
    "--steps-per-eval": int,
    "--val-batches": int,
    "--save-every": int,
    "--adapter-path": str,
    "--batch-size": int,
    "--grad-accumulation-steps": int,
}


def run(args: types.SimpleNamespace, callback: TrainingCallback) -> None:
    """Replique `mlx_lm.lora.run` (0.32.2) com o nosso callback.

    O `run` da biblioteca descarta o callback recebido e só aceita os de `report_to`.
    """
    np.random.seed(args.seed)
    model, tokenizer = load(args.model, tokenizer_config={"trust_remote_code": False})
    train_set, valid_set, test_set = load_dataset(args, tokenizer)
    train_model(args, model, train_set, valid_set, callback)
    if args.test:
        evaluate_model(args, model, test_set)


class Recorder(TrainingCallback):
    """Grave cada relatório do treinador em treino-metricas.jsonl."""

    def __init__(self, path: Path):
        self.stream = path.open("a", encoding="utf-8")

    def _write(self, event: str, info: dict) -> None:
        row = {"event": event, **info}
        self.stream.write(json.dumps(row, default=float) + "\n")
        self.stream.flush()

    def on_train_loss_report(self, train_info: dict) -> None:
        self._write("train", train_info)

    def on_val_loss_report(self, val_info: dict) -> None:
        self._write("val", val_info)


def summarize(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    train = [r for r in rows if r["event"] == "train"]
    val = [r for r in rows if r["event"] == "val"]
    return {
        "train_reports": len(train),
        "final_train_loss": train[-1]["train_loss"] if train else None,
        "val_losses": [{"iteration": r["iteration"], "val_loss": r["val_loss"]} for r in val],
        "peak_memory_gb": max((r["peak_memory"] for r in train), default=None),
        "mean_tokens_per_sec": (
            sum(r["tokens_per_second"] for r in train) / len(train) if train else None
        ),
        "trained_tokens": train[-1]["trained_tokens"] if train else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    parser.add_argument("--test", action="store_true", help="Avalie o split de teste ao final.")
    parser.add_argument("--grad-checkpoint", action="store_true", default=None)
    for flag, kind in OVERRIDES.items():
        parser.add_argument(flag, type=kind)
    cli = parser.parse_args()

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    preset = yaml.load(cli.config.read_text(encoding="utf-8"), yaml_loader)
    args = dict(preset)
    for flag in OVERRIDES:
        key = flag.removeprefix("--").replace("-", "_")
        if getattr(cli, key) is not None:
            args[key] = getattr(cli, key)
    if cli.grad_checkpoint:
        args["grad_checkpoint"] = True
    if cli.test:
        args["test"] = True
    for key, value in CONFIG_DEFAULTS.items():
        args.setdefault(key, value)

    if args.get("disable_thinking"):
        template = load_tokenizer(Path(args["model"]), {"trust_remote_code": False}).chat_template
        if not (template or "").startswith(NON_THINKING_PREFIX):
            parser.error("O tokenizer do modelo está sem o template non-thinking. Treino abortado.")
    adapter = Path(args["adapter_path"])
    output = cli.runs_dir / cli.run_id
    if adapter.exists():
        parser.error(f"O adaptador já existe: {adapter}. Escolha outro diretório.")
    output.mkdir(parents=True, exist_ok=False)
    data = Path(args["data"])
    effective = {
        "run_id": cli.run_id,
        "preset": cli.config.as_posix(),
        "preset_sha256": sha256(cli.config),
        "effective_args": {k: v for k, v in args.items() if v is not None},
        "overrides": {
            k: args[k]
            for k in (f.removeprefix("--").replace("-", "_") for f in OVERRIDES)
            if getattr(cli, k) is not None
        },
        "pissa": json.loads((Path(args["model"]).parent / "pissa.json").read_text())
        if (Path(args["model"]).parent / "pissa.json").is_file()
        else None,
        "data": {
            s: {"path": str(data / f"{s}.jsonl"), "sha256": sha256(data / f"{s}.jsonl")}
            for s in ("train", "valid", "test")
        },
        "grad_checkpoint_flag": bool(cli.grad_checkpoint),
        "command": sys.argv,
        **environment(),
    }
    init = args.get("resume_adapter_file")
    if init:
        effective["init_adapter_sha256"] = sha256(Path(init))
    (output / "config-efetiva.json").write_text(
        json.dumps(effective, ensure_ascii=False, indent=1) + "\n"
    )

    metrics_path = output / "treino-metricas.jsonl"
    started = time.time()
    run(types.SimpleNamespace(**args), Recorder(metrics_path))
    summary = summarize(metrics_path)
    summary["wall_seconds"] = time.time() - started
    summary["process_peak_memory_gb"] = mx.get_peak_memory() / 1e9
    summary["adapter_sha256"] = sha256(adapter / "adapters.safetensors")
    (output / "treino-resumo.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n"
    )
    print(
        f"Rodada {cli.run_id}: pico {summary['peak_memory_gb']} GB, "
        f"{summary['mean_tokens_per_sec']} tokens/s, {summary['wall_seconds']:.0f} s. "
        f"Registro em {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
