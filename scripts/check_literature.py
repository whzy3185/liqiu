"""Validate corpus identity, evidence labels, and matrix alignment."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with (ROOT / "literature/papers.csv").open(encoding="utf-8") as handle:
        papers = list(csv.DictReader(handle))
    with (ROOT / "taxonomy/component_matrix.csv").open(encoding="utf-8") as handle:
        components = list(csv.DictReader(handle))
    json_rows = [
        json.loads(line)
        for line in (ROOT / "literature/papers.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(papers) >= 100, f"only {len(papers)} papers"
    assert len(papers) == len(components) == len(json_rows)
    assert len({row["paper_id"] for row in papers}) == len(papers)
    assert len({row["title"].casefold() for row in papers}) == len(papers)
    dois = [row["doi"] for row in papers if row["doi"]]
    assert len(set(dois)) == len(dois)
    assert sum(2019 <= int(row["year"]) <= 2026 for row in papers) >= 100
    assert {row["paper_id"] for row in papers} == {row["paper_id"] for row in components}
    assert all(row["evidence_level"] in {"metadata-only", "abstract-coded"} for row in components)
    assert all("abstract" not in row for row in json_rows), "abstract text must not be redistributed"
    print(
        f"Literature verification passed: {len(papers)} unique records; "
        f"{sum(row['evidence_level'] == 'abstract-coded' for row in components)} abstract-coded."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

