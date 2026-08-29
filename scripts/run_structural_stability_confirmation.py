"""Run the pre-frozen structural stability confirmation matrix."""

from __future__ import annotations

from pathlib import Path

from studies.structural_stability.confirmation import evaluate


def main() -> None:
    output = Path("results/structural_stability_confirmation.csv")
    frame = evaluate()
    frame.to_csv(output, index=False)
    print({"status": "DONE", "rows": len(frame), "output": str(output)})


if __name__ == "__main__":
    main()
