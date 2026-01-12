from __future__ import annotations

import json
from pathlib import Path

from paperops.checks.models import Issue
from paperops.papers import load_paper_config
from paperops.utils import sha256_file


def check(repo_root: Path, paper_dir: Path, paper_id: str, mode: str) -> list[Issue]:
    config = load_paper_config(paper_dir / "paperops.yml")
    auto_dir = paper_dir / config["paths"]["auto_dir"]
    manifest_path = auto_dir / "MANIFEST.json"
    if not manifest_path.exists():
        fix = f"uv run paperops build-paper-assets --paper {paper_id}"
        recheck = f"uv run paperops check --paper {paper_id} --mode {mode}"
        return [
            Issue(
                category="FRESHNESS",
                severity="FAIL",
                message=(
                    f"Missing papers/{paper_id}/auto/MANIFEST.json; "
                    "run build-paper-assets."
                ),
                fix=fix,
                recheck=recheck,
                paths=[str(manifest_path)],
            )
        ]

    manifest = json.loads(manifest_path.read_text())
    metrics_path = repo_root / manifest["source"]["metrics_json_path"]
    if not metrics_path.exists():
        fix = "uv run paperops run exp=example"
        recheck = f"uv run paperops check --paper {paper_id} --mode {mode}"
        return [
            Issue(
                category="FRESHNESS",
                severity="FAIL",
                message=f"Missing metrics.json for {paper_id}: {metrics_path}",
                fix=fix,
                recheck=recheck,
                paths=[str(metrics_path)],
            )
        ]
    expected = manifest["source"]["metrics_json_sha256"]
    actual = sha256_file(metrics_path)
    if actual != expected:
        fix = f"uv run paperops build-paper-assets --paper {paper_id}"
        recheck = f"uv run paperops check --paper {paper_id} --mode {mode}"
        return [
            Issue(
                category="FRESHNESS",
                severity="FAIL",
                message=f"Paper assets are stale for {paper_id}; run build-paper-assets.",
                fix=fix,
                recheck=recheck,
                paths=[str(manifest_path), str(metrics_path)],
            )
        ]
    return []
