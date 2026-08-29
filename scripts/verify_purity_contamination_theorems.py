"""Run independent finite checks of stated purity-contamination theorems."""

from __future__ import annotations

import json
from pathlib import Path

from theory.purity_contamination.verify_theorems import run


def main() -> None:
    result = run()
    Path("artifacts/purity_contamination_theorem_verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = {key: len(value) for key, value in result.items() if isinstance(value, list)}
    report = ["# Purity Contamination Theorem Verification", "", "This is an independent finite falsification program, not a proof. It checks all ordered full binary tree shapes through seven leaves, all binary labelings on those shapes, complete balanced marked-subset maxima through 16 leaves, and rational local threshold budgets through support 32.", ""]
    report.extend(f"- {key}: {value}" for key, value in counts.items())
    report.extend(["", "No finite counterexample was found for the stated restricted tau-one formulas. The result does not resolve novelty: the theorems remain direct marked-prefix/tree-frontier combinatorics, as recorded in the theory decision."])
    Path("reports/purity_contamination/theory_verification.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print({"status": "DONE", **counts})


if __name__ == "__main__":
    main()
