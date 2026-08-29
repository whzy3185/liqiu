"""Run the exact small-tree counterexample search for the purity theory line."""

from __future__ import annotations

import json
from pathlib import Path

from theory.purity_contamination.enumerate import run


def main() -> None:
    result = run()
    output = Path("artifacts/purity_contamination_enumeration.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = ["# Purity Contamination Enumeration Baseline", "", "The program exhaustively tests all ordered full binary tree shapes through seven leaves for the single-flip formula, and all marked-leaf subsets of complete binary trees through 16 leaves for the balanced-tree maximum candidate. It also enumerates binary labelings on one canonical shape through six leaves at rational thresholds 1/2, 2/3, 3/4, and 1.", "", f"- Single-flip exact-formula counterexamples: {len(result['single_flip_exact_formula_failures'])}", f"- Balanced-tree maximum-candidate counterexamples: {len(result['balanced_max_candidate_failures'])}", f"- Non-unit-threshold exact examples recorded: {result['tau_example_count']}", "", "These checks do not prove the claims. They only failed to falsify the stated tau=1 candidates within their exhaustive range. Non-unit thresholds remain a separate activation-cascade problem."]
    Path("reports/purity_contamination").mkdir(parents=True, exist_ok=True)
    Path("reports/purity_contamination/enumeration_baseline.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print({"status": "DONE", **{key: len(value) if isinstance(value, list) else value for key, value in result.items()}})


if __name__ == "__main__":
    main()
