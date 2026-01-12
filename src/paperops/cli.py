from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
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
from paperops.papers import get_paper_by_id, write_discovery_manifest
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


def _load_pipeline_config(repo_root: Path) -> dict[str, Any]:
    pipeline_path = repo_root / "conf" / "pipeline.yaml"
    if not pipeline_path.exists():
        return {}
    cfg = OmegaConf.load(pipeline_path)
    data = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(data, dict):
        return {}
    return data


def _resolve_metrics_source(repo_root: Path, metrics_source: str | None) -> Path:
    pipeline = _load_pipeline_config(repo_root)
    latest_cfg = pipeline.get("latest", {}) if isinstance(pipeline, dict) else {}
    runs_dir = repo_root / latest_cfg.get("runs_dir", "runs")

    if metrics_source in (None, "latest"):
        run_dir = find_latest_run(runs_dir)
        if run_dir is None:
            raise SystemExit("No runs found. Execute a run first.")
        return run_dir

    run_dir = runs_dir / metrics_source
    if not run_dir.exists():
        raise SystemExit(f"Run not found: {run_dir}")
    return run_dir


def _build_paper_assets(paper_id: str) -> None:
    repo_root = _repo_root()
    paper = get_paper_by_id(repo_root, paper_id)
    paper_dir = repo_root / paper["paper_dir"]
    inputs = paper.get("inputs", {}) if isinstance(paper.get("inputs"), dict) else {}
    metrics_source = inputs.get("metrics_source")

    run_dir = _resolve_metrics_source(repo_root, metrics_source)
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        raise SystemExit(f"Missing metrics.json in {run_dir}")

    metrics = json.loads(metrics_path.read_text())

    auto_dir = paper_dir / "auto"
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
            "paper_id": paper_id,
            "run_dir": str(run_dir.relative_to(repo_root)),
            "metrics_source": metrics_source or "latest",
            "metrics_json_path": str(metrics_path.relative_to(repo_root)),
            "metrics_json_sha256": sha256_file(metrics_path),
        },
        "generated": {
            "variables_tex_sha256": sha256_file(variables_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    write_json(auto_dir / "MANIFEST.json", manifest)


def _build_paper(paper_id: str) -> None:
    repo_root = _repo_root()
    paper = get_paper_by_id(repo_root, paper_id)
    paper_dir = repo_root / paper["paper_dir"]
    main_path = paper_dir / paper.get("main", "main.tex")
    if not main_path.exists():
        raise SystemExit(f"Missing main tex for {paper_id}: {main_path}")

    engine = paper.get("engine", "latexmk")
    output_dir = paper_dir / "build"
    ensure_dir(output_dir)

    if isinstance(engine, str):
        engine_cmd = engine
    else:
        raise SystemExit(f"Invalid engine for paper {paper_id}")

    if engine_cmd == "latexmk":
        cmd = [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory",
            str(output_dir),
            str(main_path),
        ]
    elif "{main}" in engine_cmd:
        cmd = shlex.split(engine_cmd.format(main=str(main_path)))
    else:
        cmd = shlex.split(engine_cmd) + [str(main_path)]

    env = os.environ.copy()
    style = paper.get("style", {}) if isinstance(paper.get("style"), dict) else {}
    texinputs = [str(paper_dir)]
    styles_dir = paper_dir / "styles"
    texinputs.append(str(styles_dir))
    extra_tex = style.get("TEXINPUTS", [])
    if isinstance(extra_tex, str):
        extra_tex = [extra_tex]
    if isinstance(extra_tex, list):
        for entry in extra_tex:
            entry_path = (paper_dir / entry).resolve() if entry else paper_dir
            texinputs.append(str(entry_path))
    texinputs_str = os.pathsep.join(texinputs) + os.pathsep + env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = texinputs_str

    subprocess.run(cmd, check=True, cwd=repo_root, env=env)


def run_command(overrides: list[str]) -> None:
    from paperops import experiments  # noqa: F401

    cfg = _load_config(overrides)
    run_dir = _resolve_run_dir(cfg)

    experiment_name = cfg.experiment.name
    experiment_cls = get_experiment_class(experiment_name)
    experiment = experiment_cls(cfg, run_dir)

    runner = ExperimentRunner(cfg, run_dir, experiment)
    runner.run()


def discover_command() -> None:
    write_discovery_manifest(_repo_root())


def build_paper_assets_command(paper_id: str) -> None:
    _build_paper_assets(paper_id)


def build_paper_command(paper_id: str) -> None:
    _build_paper(paper_id)


def check_command(paper_id: str | None) -> None:
    repo_root = _repo_root()
    check_run_integrity.check(repo_root / "runs")
    if paper_id:
        paper = get_paper_by_id(repo_root, paper_id)
        paper_dir = repo_root / paper["paper_dir"]
        check_paper_freshness.check(repo_root, paper_dir, paper_id)
        tex_path = paper_dir / paper.get("main", "main.tex")
        check_no_manual_numbers.check(tex_path)
        return

    manifest = write_discovery_manifest(repo_root)
    data = json.loads(manifest.read_text())
    for paper in data.get("papers", []):
        pid = paper["paper_id"]
        paper_dir = repo_root / paper["paper_dir"]
        check_paper_freshness.check(repo_root, paper_dir, pid)
        tex_path = paper_dir / paper.get("main", "main.tex")
        check_no_manual_numbers.check(tex_path)


def main() -> None:
    parser = argparse.ArgumentParser(prog="paperops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("overrides", nargs=argparse.REMAINDER)

    subparsers.add_parser("discover", help="Discover papers")

    assets_parser = subparsers.add_parser(
        "build-paper-assets", help="Generate paper assets"
    )
    assets_parser.add_argument("--paper", required=True)

    build_parser = subparsers.add_parser("build-paper", help="Build a paper")
    build_parser.add_argument("--paper", required=True)

    check_parser = subparsers.add_parser("check", help="Run checks")
    check_parser.add_argument("--paper")

    args = parser.parse_args()

    if args.command == "run":
        overrides = [arg for arg in args.overrides if arg]
        run_command(overrides)
    elif args.command == "discover":
        discover_command()
    elif args.command == "build-paper-assets":
        build_paper_assets_command(args.paper)
    elif args.command == "build-paper":
        build_paper_command(args.paper)
    elif args.command == "check":
        check_command(args.paper)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
