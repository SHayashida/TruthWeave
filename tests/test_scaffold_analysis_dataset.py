from __future__ import annotations

from pathlib import Path

import pytest

from truthweave.cli import create_analysis_command, create_dataset_command


def test_create_analysis_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "src" / "truthweave" / "analysis").mkdir(parents=True)
    monkeypatch.setenv("TRUTHWEAVE_REPO_ROOT", str(tmp_path))

    create_analysis_command("my_analysis", None)

    target = tmp_path / "src" / "truthweave" / "analysis" / "my_analysis.py"
    content = target.read_text()
    assert "def main()" in content
    assert "artifacts" in content


def test_create_dataset_creates_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "data").mkdir(parents=True)
    monkeypatch.setenv("TRUTHWEAVE_REPO_ROOT", str(tmp_path))

    create_dataset_command("mydata")

    meta = tmp_path / "data" / "raw" / "mydata" / "DATASET.md"
    assert meta.exists()
