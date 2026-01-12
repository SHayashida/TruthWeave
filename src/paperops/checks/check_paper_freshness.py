from __future__ import annotations

import json
from pathlib import Path

from paperops.utils import sha256_file


def check(repo_root: Path) -> None:
    manifest_path = repo_root / "paper" / "auto" / "MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit("Missing paper/auto/MANIFEST.json; run build-paper-assets.")

    manifest = json.loads(manifest_path.read_text())
    metrics_path = repo_root / manifest["source"]["metrics_json_path"]
    expected = manifest["source"]["metrics_json_sha256"]
    actual = sha256_file(metrics_path)
    if actual != expected:
        raise SystemExit("Paper assets are stale; run build-paper-assets.")
