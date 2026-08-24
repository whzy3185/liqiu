"""Dependency-free deterministic smoke runner used to verify TASK 0."""

from __future__ import annotations

import random
from typing import Any, Dict, Mapping


def run(config: Mapping[str, Any]) -> Dict[str, Any]:
    rng = random.Random(int(config["seed"]))
    values = [rng.random() for _ in range(20)]
    predicted = [int(value >= 0.5) for value in values]
    labels = [int(index % 2 == 0) for index in range(20)]
    accuracy = sum(a == b for a, b in zip(predicted, labels)) / len(labels)
    return {
        "metrics": {
            "accuracy": accuracy,
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {"deterministic_checksum": round(sum(values), 12)},
        },
        "structure": {
            "granule_count": 2,
            "average_granule_size": 10.0,
            "uncertain_sample_ratio": 0.0,
            "additional": {"runner": "smoke"},
        },
        "outcome": "success",
        "notes": "Infrastructure smoke test; not scientific evidence.",
    }

