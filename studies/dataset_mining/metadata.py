"""Metadata writer utilities; structural outcome fields do not belong here."""

from __future__ import annotations

import csv
from pathlib import Path

from .catalog import CATALOG_COLUMNS, CatalogEntry


def write_catalog(path: Path, entries: list[CatalogEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CATALOG_COLUMNS)
        writer.writeheader()
        writer.writerows(entry.row() for entry in entries)
