"""Discrete provenance, saturation, and comparability profiles; no composite score."""

from __future__ import annotations


def validate_entry_status(entry: dict[str, object]) -> list[str]:
    required = ("source_dataset_id", "dataset_name", "original_url", "target_definition", "provenance_status", "status")
    return [name for name in required if not entry.get(name)]


def profile_label(status: str) -> str:
    if status == "DOWNLOAD_APPROVED":
        return "HIGH"
    if status.startswith("METADATA_REJECTED"):
        return "LOW"
    return "MEDIUM"
