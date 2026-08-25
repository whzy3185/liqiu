"""Freeze the first application-map edge test: spatial sensor placement."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("smooth_multiscale", "anisotropic", "discontinuous", "local_hotspots")
SEEDS = (1, 7, 21, 42, 2026)


def main():
    output = ROOT / "experiments/configs/application_exploration/sensor_placement_v1"
    output.mkdir(parents=True, exist_ok=True)
    for family in FAMILIES:
        for seed in SEEDS:
            experiment_id = f"appsensor-{family}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-sensor-placement",
                "algorithm": "gb-spatial-monitoring-network-thinning",
                "dataset": f"synthetic-spatial-field-{family}",
                "dataset_generation_parameters": {"family": family, "sites": 400},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_sensor_placement:run",
                "hyperparameters": {"sensor_fractions": [0.05, 0.10, 0.20]},
                "search": {"enabled": False, "campaign": "app_sensor_placement_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(FAMILIES) * len(SEEDS)} sensor-placement configs")


if __name__ == "__main__":
    main()
