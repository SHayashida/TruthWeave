from __future__ import annotations

import random
from statistics import mean

from truthweave.registry import register_experiment
from truthweave.runner import BaseExperiment


@register_experiment("example")
class ExampleExperiment(BaseExperiment):
    def setup(self) -> None:
        self.n = int(self.cfg.example.n)

    def run(self) -> dict[str, float | int]:
        samples = [random.random() for _ in range(self.n)]
        avg = mean(samples)
        return {
            "mean": avg,
            "n": self.n,
        }

    def teardown(self) -> None:
        pass
