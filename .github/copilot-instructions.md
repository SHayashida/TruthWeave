# PaperOps Coding Rules

Repo rule: DO NOT create new top-level directories or move files.
Allowed new files/dirs are ONLY:
- conf/exp/*
- src/paperops/experiments/*
- papers/<paper_id>/*
- tests/*
Everything else must be edited in-place.

Before coding:
1) Print the list of files you will modify/add.
2) If you need a new path not listed above, STOP and propose the minimal change without creating it.

Implementation must pass:
- uv run paperops check
- uv run pytest -q
- (if exists) uv run paperops check-structure

- Add new experiments by creating a new `conf/exp/*.yaml` config.
- All experiments must inherit from `BaseExperiment`.
- Do not hardcode device/seed/dtype/paths in experiment code.
- Write outputs only under the resolved `run_dir`.
- Experiments return metrics as a dict; the runner saves `metrics.json`.
- Papers live under `papers/<paper_id>/` and must include `paperops.yml`.
