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

## How to add experiments (use create-exp)

```bash
uv run paperops create-exp myexp
uv run paperops run exp=myexp
```

## Workflow: add experiment

1) `uv run paperops create-exp myexp`
2) Ask AI to edit ONLY the created files
3) `uv run paperops run exp=myexp`

## Workflow: add analysis

1) `uv run paperops create-analysis my_analysis`
2) Ask AI to edit ONLY the created file
3) `make analysis NAME=my_analysis`

## Workflow: add dataset

1) `uv run paperops create-dataset mydata`
2) Place raw files into `data/raw/mydata/`

## AI prompt template

```
You are editing this repo.
Allowed files to edit:
- <list paths from scaffold output>
Do not create new directories; CI will fail.
```

## Check modes

- `paperops check` defaults to dev mode (STRUCTURE/PAPER_NUMBERS warn only).
- `paperops check --mode ci` treats STRUCTURE/PAPER_NUMBERS as failures.

## B運用（投稿先ごと）最短手順

```bash
uv run paperops create-paper demo_paper
uv run paperops run exp=example
uv run paperops build-paper-assets --paper demo_paper
uv run paperops build-paper --paper demo_paper
uv run paperops check --paper demo_paper
make assets-all
make paper-all
make check-all
```

## Pipeline config

- `conf/pipeline.yaml` defines what counts as the latest run and which sources flow into assets.
