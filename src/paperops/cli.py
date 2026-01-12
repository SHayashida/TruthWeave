from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import hydra
from omegaconf import OmegaConf

from paperops.checks import (
    check_no_manual_numbers,
    check_paper_freshness,
    check_run_integrity,
)
from paperops.registry import get_experiment_class
from paperops.runner import ExperimentRunner
from paperops.utils import ensure_dir, find_latest_run, sha256_file, write_json


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_config(overrides: list[str]) -> Any:
    config_dir = _repo_root() / "conf"
    with hydra.initialize_config_dir(config_dir=str(config_dir), version_base=None):
        cfg = hydra.compose(config_name="base", overrides=overrides)
    return cfg


def _resolve_run_dir(cfg: Any) -> Path:
    runs_dir = _repo_root() / cfg.project.runs_dir
    run_subdir = OmegaConf.to_container(cfg, resolve=True)["experiment"][
        "output_subdir"
    ]
    return runs_dir / str(run_subdir)


def _format_metric_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _metric_macro_name(key: str) -> str:
    parts = [p for p in key.replace("-", "_").split("_") if p]
    return "Metric" + "".join(part.capitalize() for part in parts)


def _build_paper_assets() -> None:
    repo_root = _repo_root()
    runs_dir = repo_root / "runs"
    run_dir = find_latest_run(runs_dir)
    if run_dir is None:
        raise SystemExit("No runs found. Execute a run first.")

    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        raise SystemExit(f"Missing metrics.json in {run_dir}")

    metrics = json.loads(metrics_path.read_text())

    auto_dir = repo_root / "paper" / "auto"
    ensure_dir(auto_dir)
    variables_path = auto_dir / "variables.tex"

    lines = []
    for key, value in metrics.items():
        macro = _metric_macro_name(key)
        formatted = _format_metric_value(value)
        lines.append(f"\\newcommand{{\\{macro}}}{{{formatted}}}")

    variables_path.write_text("\n".join(lines) + "\n")

    manifest = {
        "source": {
            "run_dir": str(run_dir.relative_to(repo_root)),
            "metrics_json_path": str(metrics_path.relative_to(repo_root)),
            "metrics_json_sha256": sha256_file(metrics_path),
        },
        "generated": {
            "variables_tex_sha256": sha256_file(variables_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    write_json(auto_dir / "MANIFEST.json", manifest)


def run_command(overrides: list[str]) -> None:
    from paperops import experiments  # noqa: F401

    cfg = _load_config(overrides)
    run_dir = _resolve_run_dir(cfg)

    experiment_name = cfg.experiment.name
    experiment_cls = get_experiment_class(experiment_name)
    experiment = experiment_cls(cfg, run_dir)

    runner = ExperimentRunner(cfg, run_dir, experiment)
    runner.run()


def build_paper_assets_command() -> None:
    _build_paper_assets()


def check_command() -> None:
    repo_root = _repo_root()
    check_run_integrity.check(repo_root / "runs")
    check_paper_freshness.check(repo_root)
    check_no_manual_numbers.check(repo_root / "paper" / "main.tex")


def main() -> None:
    parser = argparse.ArgumentParser(prog="paperops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("overrides", nargs=argparse.REMAINDER)

    subparsers.add_parser("build-paper-assets", help="Generate paper assets")
    subparsers.add_parser("check", help="Run checks")

    args = parser.parse_args()

    if args.command == "run":
        overrides = [arg for arg in args.overrides if arg]
        run_command(overrides)
    elif args.command == "build-paper-assets":
        build_paper_assets_command()
    elif args.command == "check":
        check_command()
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
