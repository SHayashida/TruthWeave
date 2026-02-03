# TruthWeave Coding Rules

Repo rule: DO NOT create new top-level directories or move files.
Allowed new files/dirs are ONLY:
- conf/exp/*
- src/truthweave/experiments/*
- papers/<paper_id>/*
- tests/*
Everything else must be edited in-place.

Before coding:
1) Print the list of files you will modify/add.
2) If you need a new path not listed above, STOP and propose the minimal change without creating it.

Implementation must pass:
- uv run truthweave check
- uv run pytest -q
- (if exists) uv run truthweave check-structure

- Add new experiments by creating a new `conf/exp/*.yaml` config.
- All experiments must inherit from `BaseExperiment`.
- Do not hardcode device/seed/dtype/paths in experiment code.
- Write outputs only under the resolved `run_dir`.
- Experiments return metrics as a dict; the runner saves `metrics.json`.
- Papers live under `papers/<paper_id>/` and must include `truthweave.yml`.
- Use `paperops create-paper` for scaffolding new papers to keep structure consistent.
- Use `paperops create-exp` to add new experiments and avoid layout drift.
- Use `paperops create-analysis` and `paperops create-dataset` for analysis/data scaffolds.

## AI Agent Skills

- Structured skills are defined in `.codex/skills/` for common TruthWeave workflows.
- Skills available: `truthweave-build-assets`, `truthweave-check` (see `.codex/skills/<skill_name>/SKILL.md`).
- When maintaining/adding skills, preserve the frontmatter format and include: Inputs, Rules, Output format, Remediation playbook.
- Skills are only editable files under `.codex/skills/**`. All other paths follow the strict edit rules above.
