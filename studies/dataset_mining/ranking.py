"""Selection helpers that intentionally avoid a weighted structural A-score."""

from __future__ import annotations


def partition_by_status(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    approved = [row for row in rows if row["status"] == "DOWNLOAD_APPROVED"]
    discovered = [row for row in rows if row["status"] == "DISCOVERED"]
    rejected = [row for row in rows if str(row["status"]).startswith("METADATA_REJECTED")]
    return {"approved": approved, "discovered": discovered, "rejected": rejected}
