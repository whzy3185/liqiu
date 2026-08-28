"""Run frozen pre-MIA diagnostics on fully downloaded approved candidates."""

from __future__ import annotations

import csv
from pathlib import Path

from studies.dataset_mining.approved_loaders import load_approved
from studies.dataset_mining.structural_profile import profile_numeric


def main() -> None:
    root = Path("datasets/real/a3_approved")
    output = Path("results/dataset_structural_profiles.csv")
    rows = []
    for source_dataset_id in ("uci-171", "uci-167", "uci-372", "uci-602"):
        x, y, note = load_approved(root, source_dataset_id)
        profile = profile_numeric(x, y)
        rows.append({"source_dataset_id": source_dataset_id, "task_id": f"{source_dataset_id}_labeled_train_validation", "parent_dataset": source_dataset_id, "profile_scope": "pre_MIA_full_labeled_train_validation", "loader_note": note, **profile})
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print({"profiles": len(rows)})


if __name__ == "__main__":
    main()
