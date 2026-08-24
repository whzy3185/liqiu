"""Generate reproducible first-pass frequency maps from the component matrix."""

from __future__ import annotations

import collections
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
UNKNOWN_PREFIXES = ("not reported", "requires full-text", "unknown", "not inferred")
AXES = ["task", "representation", "granulation", "uncertainty", "decision", "downstream", "noise"]


def values(cell: str) -> Iterable[str]:
    for value in (part.strip() for part in cell.split(";")):
        if value and not value.startswith(UNKNOWN_PREFIXES):
            yield value


def counts(rows: Sequence[Mapping[str, str]], field: str) -> collections.Counter:
    return collections.Counter(value for row in rows for value in values(row[field]))


def signature(row: Mapping[str, str]) -> str:
    parts = []
    for field in ("representation", "granulation", "decision", "downstream"):
        known = list(values(row[field]))
        parts.append(" + ".join(known) if known else "unresolved")
    return " → ".join(parts)


def table(counter: collections.Counter, limit: int = 12) -> List[str]:
    lines = ["| Component | Papers |", "|---|---:|"]
    lines.extend(f"| {name.replace('|', '/')} | {number} |" for name, number in counter.most_common(limit))
    return lines


def main() -> int:
    with (ROOT / "taxonomy/component_matrix.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit("component matrix is empty")

    evidence = collections.Counter(row["evidence_level"] for row in rows)
    signatures = collections.Counter(signature(row) for row in rows)
    report = [
        "# Research map", "", "## Scope and evidence boundary", "",
        f"This first-pass map covers **{len(rows)}** deduplicated papers: "
        f"**{evidence['abstract-coded']}** abstract-coded and **{evidence['metadata-only']}** metadata-only.",
        "Counts reflect controlled title/abstract tags, not completed full-text reviews. In",
        "particular, missing split/merge/stop criteria must not be interpreted as absence of those",
        "mechanisms in the paper.", "",
    ]
    for axis in AXES:
        report += [f"## {axis.replace('_', ' ').title()}", ""] + table(counts(rows, axis)) + [""]
    report += ["## Repeated component signatures", "", "| Signature | Papers |", "|---|---:|"]
    report += [
        f"| {name.replace('|', '/')} | {number} |"
        for name, number in signatures.most_common(15)
    ]
    report += [
        "", "## What can already be said", "",
        "1. Granular-ball rough/neighborhood-rough representations, feature selection, and",
        "   three-way decisions recur often enough to warrant a dedicated collision cluster.",
        "2. Many records cannot yet be distinguished at split/merge/stop level. A claim that",
        "   papers merely swap one component would therefore be premature.",
        "3. Agent, RAG, conformal calibration, and OOD intersections did not enter the retained",
        "   top corpus in material numbers under the high-precision title filter. This is a search",
        "   gap, not evidence of novelty; each needs a separate problem-oriented collision search.",
        "4. The sharp 2024–2026 rise in retained records makes 2026 source verification especially",
        "   important before novelty judgments.", "",
        "## Required full-text audit", "",
        "Upgrade representative papers in each high-frequency signature and explicitly extract",
        "split, merge, stop, uncertainty, datasets, baselines, gains, author limitations, and code.",
        "Only after that audit should repeated introductions be used to infer a common structural",
        "defect or to answer why generation algorithms keep being proposed.",
    ]
    (ROOT / "taxonomy/research_map.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    occupied = [
        "# Occupied topics", "", "## First-pass collision clusters", "",
        "These clusters are discovery warnings, not final novelty verdicts.", "",
    ]
    title_clusters: Dict[str, Tuple[str, ...]] = {
        "Granular-ball rough/neighborhood rough sets": ("granular ball", "rough set"),
        "Granular-ball feature/attribute selection": ("granular ball", "feature selection"),
        "Granular-ball three-way decisions": ("granular ball", "three way"),
        "Sequential three-way decisions": ("sequential", "three way"),
        "Multigranulation rough sets": ("multigranulation", "rough set"),
        "Neighborhood rough-set feature selection": ("neighborhood rough", "feature selection"),
    }
    for label, tokens in title_clusters.items():
        matches = [row for row in rows if all(token in row["paper"].lower().replace("-", " ") for token in tokens)]
        occupied += [f"### {label} ({len(matches)} records)", ""]
        occupied += [f"- {row['paper']} ({row['year']})" for row in matches[:12]] or ["- No retained title-level matches."]
        if len(matches) > 12:
            occupied.append(f"- …and {len(matches) - 12} more in `component_matrix.csv`.")
        occupied.append("")
    occupied += [
        "## Interpretation rule", "",
        "A candidate that falls in one of these clusters requires component-level and mathematical",
        "equivalence checking. Renaming a known combination does not clear the novelty gate.",
    ]
    (ROOT / "literature/occupied_topics.md").write_text("\n".join(occupied) + "\n", encoding="utf-8")
    print(f"Generated research map and occupied-topic clusters from {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

