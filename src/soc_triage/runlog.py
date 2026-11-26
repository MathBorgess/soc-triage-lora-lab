"""Auxiliares para registrar execuções em runs/: hashes, estado do Git e versões da stack."""

import hashlib
import importlib.metadata
import platform
import subprocess
from pathlib import Path

STACK = ("mlx", "mlx-lm", "transformers", "pydantic", "scikit-learn", "huggingface-hub")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_state() -> dict:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout

    return {"commit": run("rev-parse", "HEAD").strip(), "dirty": bool(run("status", "--short"))}


def environment() -> dict:
    return {
        "stack": {name: importlib.metadata.version(name) for name in STACK},
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git": git_state(),
    }
