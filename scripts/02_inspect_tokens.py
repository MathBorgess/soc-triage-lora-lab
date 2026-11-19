"""Inspecione o comprimento dos registros de chat sem carregar pesos."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml
from huggingface_hub import snapshot_download
from mlx_lm.tuner.datasets import ChatDataset
from mlx_lm.utils import load_tokenizer

SPLITS = ("train", "valid", "test")
HISTOGRAM_STEP = 128
TOKENIZER_FILES = (
    "added_tokens.json",
    "chat_template.jinja",
    "config.json",
    "merges.txt",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer.model",
    "tokenizer_config.json",
    "vocab.json",
)


def read_config(path: Path) -> tuple[str, Path, int]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise TypeError("O arquivo deve conter um mapa de configuração MLX.")
    model, data, limit = (config.get(key) for key in ("model", "data", "max_seq_length"))
    if not isinstance(model, str) or not model or not isinstance(data, str) or not data:
        raise ValueError("A configuração deve definir model e data como texto não vazio.")
    if type(limit) is not int or limit < 2:
        raise ValueError("A configuração deve definir max_seq_length como inteiro >= 2.")
    return model, Path(data), limit


def valid_chat(record: object) -> bool:
    if not isinstance(record, dict):
        return False
    messages = record.get("messages")
    roles = ("system", "user", "assistant")
    return (
        isinstance(messages, list)
        and len(messages) == len(roles)
        and all(
            isinstance(message, dict)
            and message.get("role") == role
            and isinstance(message.get("content"), str)
            and bool(message["content"].strip())
            for message, role in zip(messages, roles, strict=True)
        )
    )


def inspect_split(path: Path, dataset: ChatDataset, limit: int) -> bool:
    histogram: Counter[int] = Counter()
    examples = invalid = truncated = largest = 0
    with path.open(encoding="utf-8") as rows:
        for line_number, line in enumerate(rows, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                record = None
            if not valid_chat(record):
                invalid += 1
                print(f"{path.name} linha {line_number} — registro de chat inválido.")
                continue
            try:
                tokens, offset = dataset.process(record)
            except (ValueError, TypeError, RuntimeError):
                invalid += 1
                print(f"{path.name} linha {line_number} — falha ao aplicar o template.")
                continue

            length = len(tokens)
            # MLX prevê tokens a partir do índice 1 e corta o lote em max_seq_length.
            start = max(offset, 1)
            completion_size = length - start
            if completion_size <= 0:
                invalid += 1
                print(f"{path.name} linha {line_number} — resposta sem tokens supervisionáveis.")
                continue

            examples += 1
            largest = max(largest, length)
            histogram[(length - 1) // HISTOGRAM_STEP] += 1
            if length > limit:
                truncated += 1
                kept_completion = max(0, limit - start)
                print(
                    f"{path.name} linha {line_number} — {length} > {limit} tokens, "
                    f"preserva {kept_completion}/{completion_size} tokens da resposta "
                    "com o sufixo do template."
                )

    print(f"{path.name} — {examples} examinados, {invalid} inválidos, {truncated} truncados.")
    if not examples:
        print(f"{path.name} — nenhum registro de chat tokenizável.")
    else:
        print(f"  Maior sequência: {largest} tokens. Limite MLX: {limit} tokens.")
        for bucket, count in sorted(histogram.items()):
            low = bucket * HISTOGRAM_STEP + 1
            high = (bucket + 1) * HISTOGRAM_STEP
            print(f"  {low:>5}–{high:<5} tokens  {count:>5} sequências")
    return examples > 0 and invalid == 0 and truncated == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="YAML do experimento MLX.")
    parser.add_argument("--split", choices=SPLITS, help="Examine somente este split.")
    parser.add_argument("--tokenizer", help="Pasta local ou ID HF. O padrão é model no YAML.")
    parser.add_argument(
        "--allow-tokenizer-download",
        action="store_true",
        help="Permita buscar apenas arquivos do tokenizer no Hugging Face Hub.",
    )
    args = parser.parse_args()
    try:
        model, data_path, limit = read_config(args.config)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        parser.error(str(error))

    splits = (args.split,) if args.split else SPLITS
    paths = [data_path / f"{split}.jsonl" for split in splits]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        parser.error("Splits ausentes — " + ", ".join(missing))

    source = args.tokenizer or model
    tokenizer_path = Path(source).expanduser()
    try:
        if not tokenizer_path.is_dir():
            tokenizer_path = Path(
                snapshot_download(
                    source,
                    allow_patterns=TOKENIZER_FILES,
                    local_files_only=not args.allow_tokenizer_download,
                )
            )
        tokenizer = load_tokenizer(tokenizer_path, {"trust_remote_code": False})
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(
            f"Tokenizer indisponível ({type(error).__name__}). "
            "Forneça uma pasta em --tokenizer ou use --allow-tokenizer-download."
        )

    # O offset é calculado pelo mesmo código usado no treino com mask_prompt.
    dataset = ChatDataset([], tokenizer, mask_prompt=True)
    results = []
    for path in paths:
        try:
            results.append(inspect_split(path, dataset, limit))
        except (OSError, UnicodeError) as error:
            print(f"{path.name} — falha de leitura ({type(error).__name__}).", file=sys.stderr)
            results.append(False)
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
