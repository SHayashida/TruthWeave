from __future__ import annotations

import json
from pathlib import Path

from paperops.papers import load_paper_config
from paperops.utils import sha256_file


def check(repo_root: Path, paper_dir: Path, paper_id: str) -> None:
    config = load_paper_config(paper_dir / "paperops.yml")
    auto_dir = paper_dir / config["paths"]["auto_dir"]
    manifest_path = auto_dir / "MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit(
            f"Missing papers/{paper_id}/auto/MANIFEST.json; run build-paper-assets."
        )

    manifest = json.loads(manifest_path.read_text())
    metrics_path = repo_root / manifest["source"]["metrics_json_path"]
    if not metrics_path.exists():
        raise SystemExit(f"Missing metrics.json for {paper_id}: {metrics_path}")
    expected = manifest["source"]["metrics_json_sha256"]
    actual = sha256_file(metrics_path)
    if actual != expected:
        raise SystemExit(
            f"Paper assets are stale for {paper_id}; run build-paper-assets."
        )
