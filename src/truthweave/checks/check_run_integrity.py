from __future__ import annotations

from pathlib import Path

from truthweave.checks.models import Issue
from truthweave.utils import find_latest_run


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


def check(runs_dir: Path, mode: str, paper_id: str | None = None) -> list[Issue]:
    run_dir = find_latest_run(runs_dir)
    if run_dir is None:
        fix = "uv run truthweave run exp=example"
        recheck = (
            f"uv run truthweave check --mode {mode}"
            + (f" --paper {paper_id}" if paper_id else "")
        )
        return [
            Issue(
                category="RUN_INTEGRITY",
                severity="FAIL",
                message="No runs found to check.",
                fix=fix,
                recheck=recheck,
                paths=[str(runs_dir)],
            )
        ]

    missing = [name for name in REQUIRED_FILES if not (run_dir / name).exists()]
    missing += [
        name for name in REQUIRED_DIRS if not (run_dir / name).is_dir()
    ]
    if missing:
        fix = "uv run truthweave run exp=example"
        recheck = (
            f"uv run truthweave check --mode {mode}"
            + (f" --paper {paper_id}" if paper_id else "")
        )
        return [
            Issue(
                category="RUN_INTEGRITY",
                severity="FAIL",
                message=f"Missing run files in {run_dir}: {', '.join(missing)}",
                fix=fix,
                recheck=recheck,
                paths=[str(run_dir / name) for name in missing],
            )
        ]
    return []
