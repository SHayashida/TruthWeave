from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path
from typing import Any

import psutil
from omegaconf import OmegaConf

from paperops.utils import write_json


def save_config_resolved(run_dir: Path, cfg: Any) -> None:
    path = run_dir / "config_resolved.yaml"
    path.write_text(OmegaConf.to_yaml(cfg, resolve=True))


def _run_capture(cmd: list[str]) -> str:
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        return ""
    return result.stdout.strip()


def save_git_status(run_dir: Path) -> None:
    commit = _run_capture(["git", "rev-parse", "HEAD"]) or "unknown"
    status = _run_capture(["git", "status", "--porcelain"])
    dirty = "dirty" if status else "clean"
    path = run_dir / "git_commit.txt"
    path.write_text(f"{commit}\n{dirty}\n")


def save_command(run_dir: Path, argv: list[str] | None = None) -> None:
    if argv is None:
        import sys

        argv = sys.argv
    path = run_dir / "command.txt"
    path.write_text(" ".join(argv) + "\n")


def save_env_freeze(run_dir: Path) -> None:
    output = _run_capture(["uv", "pip", "freeze"]) or "uv pip freeze failed"
    path = run_dir / "env_freeze.txt"
    path.write_text(output + "\n")


def save_hardware_info(run_dir: Path) -> None:
    info: dict[str, Any] = {
        "platform": platform.platform(),
        "uname": platform.uname()._asdict(),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "memory_total_bytes": psutil.virtual_memory().total,
    }

    gpu_info = _run_capture(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    info["gpu"] = [line.strip() for line in gpu_info.splitlines() if line.strip()]

    try:
        import torch

        info["cuda_version"] = torch.version.cuda
    except Exception:
        info["cuda_version"] = None

    write_json(run_dir / "hardware.json", info)


def save_seeds(run_dir: Path, seed_dict: dict[str, int]) -> None:
    write_json(run_dir / "seeds.json", seed_dict)
