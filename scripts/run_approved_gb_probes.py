"""Run pre-MIA purity-trajectory structure probes for approved candidates."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from studies.dataset_mining.approved_loaders import load_approved
from studies.dataset_mining.gb_probe import probe_granular_structure
from studies.dataset_mining.structural_profile import prepare_numeric


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["source_dataset_id"] for row in csv.DictReader(handle)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+", default=["uci-171", "uci-167", "uci-372", "uci-602", "uci-253"])
    parser.add_argument("--output", type=Path, default=Path("results/dataset_gb_structure_probes.csv"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    seen = existing_ids(args.output) if args.resume else set()
    root = Path("datasets/real/a3_approved")
    for source_dataset_id in args.ids:
        if source_dataset_id in seen:
            print({"status": "SKIP_COMPLETE", "source_dataset_id": source_dataset_id})
            continue
        x, y, note = load_approved(root, source_dataset_id)
        rows = [
            {"source_dataset_id": source_dataset_id, "task_id": f"{source_dataset_id}_labeled_train_validation", "parent_dataset": source_dataset_id, "probe_scope": "pre_MIA_training_structure_only", "loader_note": note, **row}
            for row in probe_granular_structure(prepare_numeric(x), y)
        ]
        header = not args.output.exists()
        with args.output.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            if header:
                writer.writeheader()
            writer.writerows(rows)
        print({"status": "DONE", "source_dataset_id": source_dataset_id, "rows": len(rows)})


if __name__ == "__main__":
    main()
