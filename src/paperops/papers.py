from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

from paperops.utils import ensure_dir, write_json


def load_paper_config(path: Path) -> dict[str, Any]:
    cfg = OmegaConf.load(path)
    data = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid paperops.yml at {path}")
    return data


def discover_papers(repo_root: Path) -> dict[str, Any]:
    papers_dir = repo_root / "papers"
    if not papers_dir.exists():
        return {"papers": [], "generated_at": datetime.now(timezone.utc).isoformat()}

    entries = []
    for config_path in sorted(papers_dir.rglob("paperops.yml")):
        paper_dir = config_path.parent
        config = load_paper_config(config_path)
        paper_id = config.get("paper_id") or paper_dir.name
        main = config.get("main", "main.tex")
        engine = config.get("engine", "latexmk")
        style = config.get("style", {})
        inputs = config.get("inputs", {})

        entries.append(
            {
                "paper_id": paper_id,
                "paper_dir": str(paper_dir.relative_to(repo_root)),
                "config_path": str(config_path.relative_to(repo_root)),
                "main": main,
                "engine": engine,
                "style": style,
                "inputs": inputs,
            }
        )

    entries.sort(key=lambda item: item["paper_id"])
    return {"papers": entries, "generated_at": datetime.now(timezone.utc).isoformat()}


def write_discovery_manifest(repo_root: Path) -> Path:
    manifest = discover_papers(repo_root)
    out_dir = repo_root / "artifacts" / "manifests"
    ensure_dir(out_dir)
    out_path = out_dir / "papers_index.json"
    write_json(out_path, manifest)
    return out_path


def get_paper_by_id(repo_root: Path, paper_id: str) -> dict[str, Any]:
    manifest = discover_papers(repo_root)
    for paper in manifest["papers"]:
        if paper["paper_id"] == paper_id:
            return paper
    raise SystemExit(f"Unknown paper_id '{paper_id}'. Run paperops discover.")
