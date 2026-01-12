from __future__ import annotations

import json
from pathlib import Path

import pytest
from omegaconf import OmegaConf

from paperops.cli import create_paper_command, discover_command
from paperops.papers import load_paper_config
from paperops.checks import check_structure


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = REPO_ROOT / "papers"


def _cleanup_paper(paper_id: str) -> None:
    target = PAPERS_DIR / paper_id
    if target.exists():
        for child in target.rglob("*"):
            if child.is_file():
                child.unlink()
        for child in sorted(target.rglob("*"), reverse=True):
            if child.is_dir():
                child.rmdir()
        target.rmdir()


def test_create_paper_creates_structure() -> None:
    paper_id = "tmp_paper_a"
    _cleanup_paper(paper_id)
    create_paper_command(paper_id, None, None)
    try:
        paper_dir = PAPERS_DIR / paper_id
        assert (paper_dir / "paperops.yml").exists()
        assert (paper_dir / "main.tex").exists()
        assert (paper_dir / "refs.bib").exists()
        assert (paper_dir / "styles" / ".gitkeep").exists()
        cfg = load_paper_config(paper_dir / "paperops.yml")
        assert cfg["paper_id"] == paper_id
    finally:
        _cleanup_paper(paper_id)


def test_create_paper_clone() -> None:
    base_id = "basepaper"
    new_id = "clonepaper"
    _cleanup_paper(base_id)
    _cleanup_paper(new_id)

    base_dir = PAPERS_DIR / base_id
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "styles").mkdir(parents=True, exist_ok=True)
    (base_dir / "auto").mkdir(parents=True, exist_ok=True)
    (base_dir / "figures").mkdir(parents=True, exist_ok=True)
    (base_dir / "tables").mkdir(parents=True, exist_ok=True)
    (base_dir / "styles" / "style.sty").write_text("% style")
    (base_dir / "auto" / "generated.txt").write_text("generated")
    config = {
        "paper_id": base_id,
        "engine": "latexmk",
        "main": "main.tex",
        "bib": "refs.bib",
        "paths": {
            "auto_dir": "auto",
            "figures_dir": "figures",
            "tables_dir": "tables",
        },
        "style": {"TEXINPUTS": ["styles", "."]},
        "build": {"latexmk_args": ["-pdf", "-interaction=nonstopmode"]},
        "inputs": {"metrics_source": "latest"},
    }
    OmegaConf.save(OmegaConf.create(config), base_dir / "paperops.yml")
    (base_dir / "main.tex").write_text("\\input{auto/variables.tex}")
    (base_dir / "refs.bib").write_text("@article{a}")

    create_paper_command(new_id, base_id, None)
    try:
        new_dir = PAPERS_DIR / new_id
        assert (new_dir / "styles" / "style.sty").exists()
        assert not (new_dir / "auto" / "generated.txt").exists()
        cfg = load_paper_config(new_dir / "paperops.yml")
        assert cfg["paper_id"] == new_id
    finally:
        _cleanup_paper(base_id)
        _cleanup_paper(new_id)


def test_discover_index_sorted() -> None:
    ids = ["zz_test", "aa_test"]
    for pid in ids:
        _cleanup_paper(pid)
        create_paper_command(pid, None, None)

    try:
        discover_command()
        index = REPO_ROOT / "artifacts" / "manifests" / "papers_index.json"
        data = json.loads(index.read_text())
        paper_ids = [p["paper_id"] for p in data["papers"]]
        assert paper_ids == sorted(paper_ids)
    finally:
        for pid in ids:
            _cleanup_paper(pid)


def test_check_structure_detects_stray_top_level(tmp_path: Path) -> None:
    contract = {
        "top_level": {"allow_dirs": ["conf"], "allow_files": []},
        "rules": {"allow_hidden": False},
    }
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    OmegaConf.save(OmegaConf.create(contract), conf_dir / "repo_contract.yml")
    (tmp_path / "stray").mkdir()

    with pytest.raises(SystemExit):
        check_structure.check(tmp_path)
