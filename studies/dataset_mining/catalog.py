"""Typed metadata-only dataset catalog for A3 discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass


CATALOG_COLUMNS = (
    "source_dataset_id", "task_id", "parent_dataset", "dataset_name", "source_type",
    "domain", "repository", "original_url", "doi", "original_paper", "license",
    "target_definition", "estimated_n", "estimated_d", "estimated_classes", "data_type",
    "group_identifier", "group_disjoint_split_required", "download_size", "provenance_status",
    "status", "source_quality", "saturation_level", "comparability_level", "notes",
)


@dataclass(frozen=True)
class CatalogEntry:
    source_dataset_id: str
    task_id: str
    parent_dataset: str
    dataset_name: str
    source_type: str
    domain: str
    repository: str
    original_url: str
    doi: str
    original_paper: str
    license: str
    target_definition: str
    estimated_n: int | None
    estimated_d: int | None
    estimated_classes: int | None
    data_type: str
    group_identifier: str
    group_disjoint_split_required: str
    download_size: str
    provenance_status: str
    status: str
    source_quality: str
    saturation_level: str
    comparability_level: str
    notes: str

    def row(self) -> dict[str, object]:
        return asdict(self)
