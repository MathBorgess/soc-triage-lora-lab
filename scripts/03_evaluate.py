"""Avalie um modelo (Run 0) ou um adaptador treinado no hold-out e registre a execução em runs/.

Carrega o modelo no mesmo processo (MLX LM sobre Metal), gera com temperatura 0 a partir da
conversa sem o alvo e pontua cada resposta com o schema Pydantic, a busca literal de IoCs e as
métricas de triagem. Cada execução grava um diretório exclusivo com a configuração efetiva, as
revisões e os hashes, as versões da stack, as métricas e as predições.

Run 0 (zero-shot, sem adaptador):
    uv run --locked python scripts/03_evaluate.py --run-id run0-valid \
        --model google/gemma-4-E4B-it --revision 4ecc2ba63bcac23ba4a767fc87025b1450f84c9c
Adaptador treinado (a base é a residual PiSSA do preset):
    uv run --locked python scripts/03_evaluate.py --run-id run2-valid \
        --preset configs/mlx/run2_qlora_all_linear.yaml
`--check-prompt` só confere, com o tokenizer, que o prompt de geração é o prefixo exato do
prompt do treino. `--limit N` avalia só os N primeiros exemplos de cada split (verificação).
"""

import argparse
import json
import sys
import time
from pathlib import Path

import yaml
from huggingface_hub import snapshot_download
from mlx_lm.tuner.datasets import ChatDataset

from soc_triage.chat_template import disable_chat_thinking
from soc_triage.evaluation import meets_targets, score_response, summarize
from soc_triage.prompts import PROMPT_VERSION
from soc_triage.runlog import environment, sha256

SPLITS = ("valid", "test")
DEFAULT_DATA = Path("data/processed/soc-triage-v12/splits")


def resolve_model(model: str, revision: str | None) -> Path:
    path = Path(model).expanduser()
    if path.is_dir():
        return path
    # Só os arquivos do modelo: README.md e .gitattributes não são necessários e podem faltar.
    patterns = ["*.json", "*.jinja", "*.safetensors", "*.model", "*.txt"]
    return Path(
        snapshot_download(model, revision=revision, allow_patterns=patterns, local_files_only=True)
    )


def read_rows(path: Path, limit: int | None) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return rows[:limit] if limit else rows


def prompt_tokens(tokenizer, messages: list[dict]) -> list[int]:
    return tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_dict=False)


def check_prompt(tokenizer, rows: list[dict]) -> int:
    """O prompt de geração deve ser o prefixo exato do que o treino mascara."""
    dataset = ChatDataset([], tokenizer, mask_prompt=True)
    mismatches = 0
    for index, row in enumerate(rows):
        tokens, offset = dataset.process(row)
        generated = prompt_tokens(tokenizer, row["messages"][:-1])
        if list(tokens[:offset]) != list(generated):
            mismatches += 1
            print(
                f"Prompt diverge na linha {index + 1}: treino {offset} tokens, geração {len(generated)}."
            )
    print(f"Prompt de geração conferido em {len(rows)} exemplos: {mismatches} divergências.")
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--run-id", required=True, help="Identificador exclusivo da execução.")
    parser.add_argument(
        "--preset", type=Path, help="YAML do experimento; define modelo e adaptador."
    )
    parser.add_argument("--model", help="Pasta local ou ID HF. Sobrescreve o model do preset.")
    parser.add_argument("--revision", help="Revisão dos pesos quando --model for um ID HF.")
    parser.add_argument("--adapter-path", type=Path, help="Pasta do adaptador treinado.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--split", action="append", choices=SPLITS, help="Padrão: valid.")
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--limit", type=int, help="Avalie só os N primeiros de cada split.")
    parser.add_argument("--check-prompt", action="store_true")
    args = parser.parse_args()

    preset: dict = {}
    if args.preset:
        preset = yaml.safe_load(args.preset.read_text(encoding="utf-8"))
    model_id = args.model or preset.get("model")
    if not model_id:
        parser.error("Informe --model ou um --preset com model.")
    adapter = args.adapter_path or (
        Path(preset["adapter_path"]) if preset.get("adapter_path") else None
    )
    if args.model and not args.adapter_path:
        adapter = None  # modelo explícito sem adaptador é zero-shot
    disable_thinking = preset.get("disable_thinking", True)
    revision = args.revision or preset.get("pissa_source_revision")
    splits = args.split or ["valid"]
    seed = int(preset.get("seed", 42))

    model_path = resolve_model(model_id, args.revision)
    if adapter is not None and not (adapter / "adapters.safetensors").is_file():
        parser.error(f"Adaptador sem adapters.safetensors: {adapter}")
    for split in splits:
        if not (args.data / f"{split}.jsonl").is_file():
            parser.error(f"Split ausente: {args.data / (split + '.jsonl')}")

    from mlx_lm.utils import load_tokenizer

    tokenizer = load_tokenizer(model_path, {"trust_remote_code": False})
    if disable_thinking:
        disable_chat_thinking(tokenizer)
    check_rows = read_rows(args.data / f"{splits[0]}.jsonl", args.limit or 20)
    mismatches = check_prompt(tokenizer, check_rows)
    if args.check_prompt:
        return 1 if mismatches else 0
    if mismatches:
        parser.error("O prompt de geração diverge do prompt do treino. Nada foi avaliado.")

    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler

    output = args.runs_dir / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    mx.random.seed(seed)
    model, tokenizer = load(str(model_path), adapter_path=str(adapter) if adapter else None)
    if disable_thinking:
        disable_chat_thinking(tokenizer)

    sampler = make_sampler(temp=0.0)
    started = time.time()
    all_records: dict[str, list[dict]] = {}
    peak_gb = 0.0
    for split in splits:
        records = []
        rows = read_rows(args.data / f"{split}.jsonl", args.limit)
        for index, row in enumerate(rows):
            messages = row["messages"]
            raw_log, target = messages[1]["content"], json.loads(messages[2]["content"])
            text, last = "", None
            for last in stream_generate(
                model,
                tokenizer,
                prompt_tokens(tokenizer, messages[:2]),
                max_tokens=args.max_tokens,
                sampler=sampler,
            ):
                text += last.text
            peak_gb = max(peak_gb, last.peak_memory if last else 0.0)
            scored = score_response(text, raw_log)
            records.append(
                {
                    "split": split,
                    "index": index,
                    "true_log_source": target["log_source"],
                    "true_verdict": target["triage"]["verdict"],
                    "response": text,
                    "prompt_tokens": last.prompt_tokens if last else 0,
                    "generation_tokens": last.generation_tokens if last else 0,
                    "generation_tps": last.generation_tps if last else 0.0,
                    "finish_reason": last.finish_reason if last else None,
                    **scored,
                }
            )
            if (index + 1) % 20 == 0:
                print(f"{split}: {index + 1}/{len(rows)}", flush=True)
        all_records[split] = records
        with (output / f"predicoes-{split}.jsonl").open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    metrics = {}
    for split, records in all_records.items():
        summary = summarize(records)
        summary["targets"] = meets_targets(summary)
        tps = [r["generation_tps"] for r in records if r["generation_tps"]]
        summary["mean_generation_tps"] = sum(tps) / len(tps) if tps else None
        metrics[split] = summary
    metrics["resources"] = {
        "peak_memory_gb": peak_gb,
        "wall_seconds": time.time() - started,
        "limit": args.limit,
    }
    (output / "metricas.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1) + "\n")
    config_path = model_path / "config.json"
    effective = {
        "run_id": args.run_id,
        "model": str(model_id),
        "model_path": str(model_path),
        "model_config_sha256": sha256(config_path) if config_path.is_file() else None,
        "source_revision": revision,
        "adapter_path": str(adapter) if adapter else None,
        "adapter_sha256": sha256(adapter / "adapters.safetensors") if adapter else None,
        "preset": args.preset.as_posix() if args.preset else None,
        "preset_sha256": sha256(args.preset) if args.preset else None,
        "disable_thinking": disable_thinking,
        "prompt_version": PROMPT_VERSION,
        "generation": {"temperature": 0.0, "max_tokens": args.max_tokens, "seed": seed},
        "data": {
            s: {"path": str(args.data / f"{s}.jsonl"), "sha256": sha256(args.data / f"{s}.jsonl")}
            for s in splits
        },
        "command": sys.argv,
        **environment(),
    }
    (output / "config-efetiva.json").write_text(
        json.dumps(effective, ensure_ascii=False, indent=1) + "\n"
    )
    for split, summary in metrics.items():
        if split == "resources":
            continue
        print(
            f"{split}: pass={summary['pydantic_pass_rate']:.3f} "
            f"ioc_halluc={summary['ioc_hallucination_rate']} "
            f"macroF1(strict)={summary['triage_strict']['macro_f1']:.3f} "
            f"FPR={summary['triage_strict']['false_positive_rate']}"
        )
    print(f"Pico de memória: {peak_gb:.1f} GB | registro em {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
