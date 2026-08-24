"""Self-contained verification for the TASK 0 research infrastructure."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_core import run_from_config


REQUIRED = [
    "literature/papers.csv", "literature/papers.jsonl",
    "taxonomy/component_matrix.csv", "experiments/configs/smoke.json",
    "datasets/registry.jsonl", "candidates/rejected.md",
    "reports/literature_report.md", "reports/baseline_report.md",
    "reports/counterexample_report.md", "reports/candidate_report.md",
    "reports/final_research_report.md",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"missing required paths: {missing}")
    with tempfile.TemporaryDirectory(prefix="task0-check-") as temp:
        output = Path(temp) / "runs.jsonl"
        first = run_from_config(ROOT / "experiments/configs/smoke.json", output)
        second = run_from_config(ROOT / "experiments/configs/smoke.json", output)
        records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        assert len(records) == 2
        assert first["additional_metrics"] == second["additional_metrics"]
        assert all(record["seed"] == 42 for record in records)
        assert all(record["outcome"] == "success" for record in records)
        assert all("git_commit" in record and "runtime_seconds" in record for record in records)
    print("TASK 0 verification passed: schema, append-only records, and determinism are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
