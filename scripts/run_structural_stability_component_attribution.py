"""Execute frozen component attribution after the structural-stability GO gate."""

from __future__ import annotations

from pathlib import Path

from studies.structural_stability.component_attribution import evaluate


def main() -> None:
    output = Path("results/structural_stability_component_attribution.csv")
    frame = evaluate()
    frame.to_csv(output, index=False)
    print({"status": "DONE", "rows": len(frame), "output": str(output)})


if __name__ == "__main__":
    main()
