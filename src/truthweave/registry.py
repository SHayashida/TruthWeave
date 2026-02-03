from __future__ import annotations

from typing import Dict, Type

from truthweave.runner import BaseExperiment

_REGISTRY: Dict[str, Type[BaseExperiment]] = {}


def register_experiment(name: str):
    def decorator(cls: Type[BaseExperiment]) -> Type[BaseExperiment]:
        _REGISTRY[name] = cls
        return cls

    return decorator


def get_experiment_class(name: str) -> Type[BaseExperiment]:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown experiment '{name}'. Available: {available}")
    return _REGISTRY[name]
