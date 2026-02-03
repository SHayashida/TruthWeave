# TruthWeave Template v1

[![CI](https://github.com/SHayashida/TruthWeave/actions/workflows/ci.yml/badge.svg)](https://github.com/SHayashida/TruthWeave/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Reproducible research workflow template for academic papers. Ensures experiments are traceable, paper metrics are automatically synced, and manual number updates are eliminated.

[日本語版 README はこちら](README.ja.md)

## Quickstart

```bash
uv sync
uv run truthweave run exp=example
uv run truthweave discover
uv run truthweave build-paper-assets --paper example
uv run truthweave check --paper example
```

## Overview

TruthWeave enforces a structured workflow for academic paper writing:

```
Experiment (conf/exp + src/truthweave/experiments)
  -> runs/
  -> artifacts/
  -> papers/<paper_id>/auto
  -> PDF
```

## Core Workflows

### Adding a New Paper

```bash
uv run truthweave create-paper <paper_id>
# Or copy from an existing paper:
uv run truthweave create-paper <paper_id> --from <base_paper_id>
```

Conference-specific `.cls`/`.sty` files should be placed in `papers/<paper_id>/styles/`.

### Adding a New Experiment

```bash
uv run truthweave create-exp <exp_name>
```

**AI Collaboration Template** (restrict editable files):

```
This repository has a fixed structure.
Allowed files to edit:
- conf/exp/<exp_name>.yaml
- src/truthweave/experiments/<exp_name>.py
Do not create or modify any other files/directories.
```

Run the experiment:

```bash
uv run truthweave run exp=<exp_name>
```

### Adding a Dataset

```bash
uv run truthweave create-dataset <dataset_id>
```

Place raw data files in `data/raw/<dataset_id>/`.

### Adding Analysis/Figures

```bash
uv run truthweave create-analysis <analysis_name>
make analysis NAME=<analysis_name>
# Or run directly:
uv run python -m truthweave.analysis.<analysis_name>
```

### Building Paper Assets

Sync metrics, figures, and tables to the paper:

```bash
uv run truthweave build-paper-assets --paper <paper_id>
```

The paper should use `\input{auto/variables.tex}` and reference macros instead of hardcoded numbers.

### Building the PDF

```bash
uv run truthweave build-paper --paper <paper_id>
```

Requires `latexmk` or similar LaTeX tools installed.

### Pre-Commit Checks

```bash
uv run truthweave check --paper <paper_id> --mode dev
uv run truthweave check --paper <paper_id> --mode ci
```

- **dev mode**: STRUCTURE/PAPER_NUMBERS produce warnings only
- **ci mode**: STRUCTURE/PAPER_NUMBERS cause failures

## Troubleshooting

| Symptom | Cause | Solution |
| --- | --- | --- |
| MANIFEST is stale | Assets not regenerated | `uv run truthweave build-paper-assets --paper <paper_id>` |
| No runs found | Experiment not executed | `uv run truthweave run exp=<exp_name>` |
| Structure check fail | Repository layout violation | Use scaffolding commands to restructure |
| Manual inline numbers detected | Hardcoded numbers in `.tex` | Replace with macros or append `% truthweave-allow-number` |

## Paper Workflow

- Papers live under `papers/<paper_id>/` with a `truthweave.yml` configuration
- `truthweave discover` scans for `truthweave.yml` and writes `artifacts/manifests/papers_index.json`
- `truthweave build-paper-assets --paper <paper_id>` writes `papers/<paper_id>/auto/variables.tex` and `papers/<paper_id>/auto/MANIFEST.json`
- `truthweave build-paper --paper <paper_id>` builds the LaTeX paper using the engine in `truthweave.yml`
- Make targets: `make assets PAPER=<paper_id>`, `make paper PAPER=<paper_id>`, `make assets-all`, `make paper-all`

## Workflow Summary: Add Experiment

1. `uv run truthweave create-exp myexp`
2. Ask AI to edit ONLY the created files
3. `uv run truthweave run exp=myexp`

## Workflow Summary: Add Analysis

1. `uv run truthweave create-analysis my_analysis`
2. Ask AI to edit ONLY the created file
3. `make analysis NAME=my_analysis`

## Workflow Summary: Add Dataset

1. `uv run truthweave create-dataset mydata`
2. Place raw files into `data/raw/mydata/`

## Codex/AI Agent Skills

This repository includes structured skills for AI agents (Codex, GitHub Copilot, etc.) in `.codex/skills/`:

### Available Skills

#### `truthweave-build-assets`
- **Purpose**: Rebuild paper assets (figures/tables/variables) deterministically for a paper_id
- **Usage**: Automatically invoked when AI needs to regenerate paper outputs
- **Key Commands**: `uv run truthweave build-paper-assets --paper <paper_id>`
- **Constraints**: Never manually edit `papers/<paper_id>/auto/`

#### `truthweave-check`
- **Purpose**: Run TruthWeave CI checks, diagnose failures, and propose fixes
- **Usage**: Automatically invoked for validation and troubleshooting
- **Key Commands**: `uv run truthweave check --paper <paper_id> --mode ci`
- **Capabilities**: Detects stale assets, missing metadata, structure violations

### Maintaining Skills

To add or modify skills:

1. Create/edit skill in `.codex/skills/<skill_name>/SKILL.md`
2. Follow the frontmatter format:
   ```yaml
   ---
   name: skill-name
   description: Brief description
   ---
   ```
3. Include: Inputs, Rules, Output format, Remediation playbook
4. Skills are automatically available to AI agents

See [AGENTS.md](AGENTS.md) for the agent contract and editing constraints.

## AI Prompt Template

When collaborating with AI agents:

```
You are editing this repo.
Allowed files to edit:
- <list paths from scaffold output>
Do not create new directories; CI will fail.
```

## Check Modes

- `truthweave check` defaults to **dev mode** (STRUCTURE/PAPER_NUMBERS warn only)
- `truthweave check --mode ci` treats STRUCTURE/PAPER_NUMBERS as failures

## Multi-Paper Workflow (Fastest Path)

```bash
uv run truthweave create-paper demo_paper
uv run truthweave run exp=example
uv run truthweave build-paper-assets --paper demo_paper
uv run truthweave build-paper --paper demo_paper
uv run truthweave check --paper demo_paper
make assets-all
make paper-all
make check-all
```

## Pipeline Configuration

`conf/pipeline.yaml` defines what counts as the latest run and which sources flow into assets.

## License

See [LICENSE](LICENSE) file for details.

