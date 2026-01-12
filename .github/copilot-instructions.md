# PaperOps Coding Rules

- Add new experiments by creating a new `conf/exp/*.yaml` config.
- All experiments must inherit from `BaseExperiment`.
- Do not hardcode device/seed/dtype/paths in experiment code.
- Write outputs only under the resolved `run_dir`.
- Experiments return metrics as a dict; the runner saves `metrics.json`.
