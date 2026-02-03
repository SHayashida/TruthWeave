from __future__ import annotations

import json
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

from truthweave import snapshot
from truthweave.utils import ensure_dir, write_json


class BaseExperiment(ABC):
    def __init__(self, cfg: Any, run_dir: Path) -> None:
        self.cfg = cfg
        self.run_dir = run_dir

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def run(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def teardown(self) -> None:
        pass


class ExperimentRunner:
    def __init__(self, cfg: Any, run_dir: Path, experiment: BaseExperiment) -> None:
        self.cfg = cfg
        self.run_dir = run_dir
        self.experiment = experiment

    def _seed_all(self) -> dict[str, int]:
        seed = int(self.cfg.runtime.seed)
        random.seed(seed)
        return {"python": seed}

    def run(self) -> dict[str, Any]:
        ensure_dir(self.run_dir)
        ensure_dir(self.run_dir / "artifacts")

        seeds = self._seed_all()
        snapshot.save_config_resolved(self.run_dir, self.cfg)
        snapshot.save_git_status(self.run_dir)
        snapshot.save_command(self.run_dir)
        snapshot.save_env_freeze(self.run_dir)
        snapshot.save_hardware_info(self.run_dir)
        snapshot.save_seeds(self.run_dir, seeds)

        self.experiment.setup()
        try:
            metrics = self.experiment.run()
        finally:
            self.experiment.teardown()

        metrics_path = self.run_dir / "metrics.json"
        write_json(metrics_path, metrics)
        return metrics


def write_config_debug(run_dir: Path, cfg: Any) -> None:
    config_path = run_dir / "config_debug.json"
    config_path.write_text(json.dumps(OmegaConf.to_container(cfg, resolve=True)))
