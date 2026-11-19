"""Interface reservada para transformar um manifesto curado em splits MLX JSONL."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interface planejada para curadoria de dados de triagem SOC.",
        epilog=(
            "A curadoria futura seguirá os grupos e rótulos aprovados pelo responsável, "
            "validará o schema e os IoCs e usará build_chat_record para montar os splits."
        ),
    )
    parser.add_argument("--manifest", required=True, type=Path, help="Manifesto local curado.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.parse_args()
    parser.error("A implementação depende da curadoria do manifesto e dos critérios de inclusão.")


if __name__ == "__main__":
    main()
