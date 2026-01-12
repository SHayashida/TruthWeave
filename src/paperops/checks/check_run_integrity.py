from __future__ import annotations

from pathlib import Path

from paperops.utils import find_latest_run


REQUIRED_FILES = [
    "config_resolved.yaml",
    "git_commit.txt",
    "command.txt",
    "env_freeze.txt",
    "hardware.json",
    "seeds.json",
    "metrics.json",
]
REQUIRED_DIRS = [
    "artifacts",
]


def check(runs_dir: Path) -> None:
    run_dir = find_latest_run(runs_dir)
    if run_dir is None:
        raise SystemExit("No runs found to check.")

    missing = [name for name in REQUIRED_FILES if not (run_dir / name).exists()]
    missing += [
        name for name in REQUIRED_DIRS if not (run_dir / name).is_dir()
    ]
    if missing:
        raise SystemExit(f"Missing run files in {run_dir}: {', '.join(missing)}")
