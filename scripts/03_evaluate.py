"""Interface reservada para avaliação via /v1/chat/completions do MLX LM."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interface planejada para avaliar triagem com o servidor MLX LM.",
        epilog=(
            "A avaliação futura enviará apenas a conversa sem o alvo, validará o JSON "
            "da resposta e registrará as métricas em um diretório exclusivo de runs/."
        ),
    )
    parser.add_argument("--dataset", required=True, type=Path, help="Split JSONL avaliado.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--model", required=True, help="Identificador do modelo servido.")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.parse_args()
    parser.error("A implementação depende do protocolo de avaliação aprovado pelo responsável.")


if __name__ == "__main__":
    main()
