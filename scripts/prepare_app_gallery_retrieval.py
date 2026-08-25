"""Freeze compressed visual/spectral gallery retrieval configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("satimage", "satellite", "covertype", "digits")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/gallery_retrieval_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appgallery-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-gallery-retrieval",
                "algorithm": "gb-fixed-slot-gallery-retrieval",
                "dataset": f"semi-real-gallery-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 2400},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_gallery_retrieval:run",
                "hyperparameters": {"gallery_fractions": [0.05, 0.10, 0.20], "top_k": 10},
                "search": {"enabled": False, "campaign": "app_gallery_retrieval_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} gallery-retrieval configs")


if __name__ == "__main__":
    main()
