"""Export one deduplicated, GPT-friendly literature catalog."""
from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "literature" / "papers.csv"
COMPONENTS = ROOT / "taxonomy" / "component_matrix.csv"
PRIVACY = ROOT / "literature" / "privacy_security_map.csv"
OUTPUT = ROOT / "literature" / "literature_catalog_for_gpt.csv"

FIELDS = [
    "record_id",
    "title",
    "year",
    "venue",
    "doi",
    "publication_status",
    "evidence_level",
    "scope",
    "task",
    "representation",
    "granulation",
    "uncertainty",
    "decision",
    "privacy_security_role",
    "three_way_role",
    "baselines",
    "unresolved_question",
    "source_url",
    "notes",
]


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _main_status(row: dict[str, str]) -> str:
    text = " ".join([row.get("doi", ""), row.get("venue", ""), row.get("title", "")]).lower()
    return "Preprint" if "arxiv" in text or "ssrn" in text else "Published/metadata record"


def main() -> int:
    papers = _read(MAIN)
    components = {row["paper_id"]: row for row in _read(COMPONENTS)}
    privacy_rows = _read(PRIVACY)
    combined: dict[str, dict[str, str]] = {}

    for paper in papers:
        component = components[paper["paper_id"]]
        combined[_title_key(paper["title"])] = {
            "record_id": paper["paper_id"],
            "title": paper["title"],
            "year": paper["year"],
            "venue": paper["venue"],
            "doi": paper["doi"],
            "publication_status": _main_status(paper),
            "evidence_level": component["evidence_level"],
            "scope": "main_corpus",
            "task": component["task"],
            "representation": component["representation"],
            "granulation": component["granulation"],
            "uncertainty": component["uncertainty"],
            "decision": component["decision"],
            "privacy_security_role": "",
            "three_way_role": "",
            "baselines": component["baseline"],
            "unresolved_question": component["suspected_weakness"],
            "source_url": paper["primary_source_url"],
            "notes": paper["notes"],
        }

    for privacy in privacy_rows:
        key = _title_key(privacy["title"])
        if key in combined:
            row = combined[key]
            row["scope"] = "main_corpus; privacy_security_map"
            row["publication_status"] = privacy["status"]
            row["privacy_security_role"] = privacy["privacy_security_role"]
            row["three_way_role"] = privacy["three_way_role"]
            row["unresolved_question"] = privacy["unresolved"]
            row["baselines"] = privacy["baselines"] or row["baselines"]
            continue
        combined[key] = {
            "record_id": privacy["paper_id"],
            "title": privacy["title"],
            "year": privacy["year"],
            "venue": privacy["venue"],
            "doi": "",
            "publication_status": privacy["status"],
            "evidence_level": "targeted privacy/security source audit",
            "scope": "privacy_security_map",
            "task": privacy["problem"],
            "representation": privacy["granular_ball_role"],
            "granulation": "",
            "uncertainty": "",
            "decision": "",
            "privacy_security_role": privacy["privacy_security_role"],
            "three_way_role": privacy["three_way_role"],
            "baselines": privacy["baselines"],
            "unresolved_question": privacy["unresolved"],
            "source_url": privacy["primary_source"],
            "notes": privacy["main_contribution"],
        }

    rows = sorted(combined.values(), key=lambda row: (-int(row["year"]), row["title"].lower()))
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} deduplicated records to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

