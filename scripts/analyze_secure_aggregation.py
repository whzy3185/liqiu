"""Apply the frozen compression and GB-specific gates for Cheap Test E."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "results" / "experiments.jsonl"
CSV = ROOT / "experiments" / "results" / "secure_aggregation_v1.csv"
DIRECTION_CSV = ROOT / "secure_aggregation" / "results.csv"
REPORT = ROOT / "reports" / "secure_aggregation_cheap_test.md"
ANALYSIS = ROOT / "secure_aggregation" / "analysis.md"
DECISION = ROOT / "secure_aggregation" / "decision.md"


def main() -> int:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    records = [record for record in records if record.get("algorithm") == "secure-aggregation-compression-v1"]
    rows = []
    for record in records:
        if record["outcome"] != "success":
            continue
        for result in record["additional_metrics"]["rows"]:
            rows.append(
                {
                    "experiment_id": record["experiment_id"],
                    "dataset": record["dataset"],
                    "seed": record["seed"],
                    "n_clients": result["n_clients"],
                    "method": result["method"],
                    **result["metrics"],
                }
            )
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "n_clients", "method"])
    frame.to_csv(CSV, index=False)
    frame.to_csv(DIRECTION_CSV, index=False)
    decision, evidence = _decide(frame)
    report = _report(frame, records, decision, evidence)
    REPORT.write_text(report, encoding="utf-8")
    ANALYSIS.write_text(report, encoding="utf-8")
    DECISION.write_text(f"# Decision\n\n{decision}\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "rows": len(frame), "decision": decision, **evidence}, indent=2))
    return 0


def _decide(frame: pd.DataFrame) -> tuple[str, dict]:
    keys = ["dataset", "seed", "n_clients"]
    gb = frame[frame.method == "granular_ball"].set_index(keys)
    km = frame[frame.method == "kmeans"].set_index(keys)
    paired = gb.join(km, lsuffix="_gb", rsuffix="_km", how="inner")
    utility_gain = paired.accuracy_gb - paired.accuracy_km
    compression_gate = (gb.m_over_n <= 0.1) & (gb.accuracy_drop_vs_raw <= 0.02)
    gb_win = utility_gain >= 0.01
    evidence = {
        "paired_runs": int(len(paired)),
        "mean_accuracy_gain_gb_minus_kmeans": float(utility_gain.mean()),
        "gb_win_fraction": float(gb_win.mean()),
        "compression_gate_fraction": float(compression_gate.mean()),
        "mean_gb_m_over_n": float(gb.m_over_n.mean()),
        "mean_gb_accuracy_drop_vs_raw": float(gb.accuracy_drop_vs_raw.mean()),
    }
    if evidence["compression_gate_fraction"] >= 0.7 and evidence["gb_win_fraction"] >= 0.7:
        return "GO", evidence
    if evidence["mean_accuracy_gain_gb_minus_kmeans"] <= 0.005 or evidence["gb_win_fraction"] < 0.4:
        return "KILL", evidence
    return "HOLD", evidence


def _report(frame: pd.DataFrame, records: list[dict], decision: str, evidence: dict) -> str:
    failures = [record for record in records if record["outcome"] != "success"]
    summary = (
        frame.groupby("method")[["accuracy", "accuracy_drop_vs_raw", "m_over_n", "communication_bytes"]]
        .mean()
        .round(4)
        .reset_index()
    )
    return f"""# Secure Aggregation Cheap Test E

## Scope

This phase tests information compression only. Communication operations and
ciphertext counts are estimates; no cryptographic privacy claim is made.
KMeans and microclusters use the same per-client prototype count as GB.

## Mean results

```text
{summary.to_string(index=False)}
```

## Gates

- Paired GB-vs-KMeans runs: {evidence['paired_runs']}
- Mean accuracy gain (GB minus KMeans): {evidence['mean_accuracy_gain_gb_minus_kmeans']:.4f}
- Fraction with at least +0.01 GB accuracy gain: {evidence['gb_win_fraction']:.3f}
- Fraction meeting `m/n <= 0.1` and raw-accuracy drop <= 0.02: {evidence['compression_gate_fraction']:.3f}
- Mean GB `m/n`: {evidence['mean_gb_m_over_n']:.4f}
- Mean GB accuracy drop versus raw: {evidence['mean_gb_accuracy_drop_vs_raw']:.4f}

Real HE/MPC implementation is permitted only if both the compression gate and
the GB-specific comparator gate survive. Failed configurations: {len(failures)}.

## Decision

**{decision}**
"""


if __name__ == "__main__":
    raise SystemExit(main())

