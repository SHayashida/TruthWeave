# PaperOps Template v0

This repository implements the PaperOps template described in `PaperOps Template v0.md`.

## Quickstart

```bash
uv sync
uv run paperops run exp=example
uv run paperops discover
uv run paperops build-paper-assets --paper example
uv run paperops check --paper example
```

## Paper workflow

- Papers live under `papers/<paper_id>/` with a `paperops.yml` configuration.
- `paperops discover` scans for `paperops.yml` and writes `artifacts/manifests/papers_index.json`.
- `paperops build-paper-assets --paper <paper_id>` writes `papers/<paper_id>/auto/variables.tex` and `papers/<paper_id>/auto/MANIFEST.json`.
- `paperops build-paper --paper <paper_id>` builds the LaTeX paper using the engine in `paperops.yml`.
- Make targets: `make assets PAPER=<paper_id>`, `make paper PAPER=<paper_id>`, `make assets-all`, `make paper-all`.

## Pipeline config

- `conf/pipeline.yaml` defines what counts as the latest run and which sources flow into assets.
