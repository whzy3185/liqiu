"""Metadata-only A3 dataset miner. Structural profiling is a separate explicit stage."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from studies.dataset_mining.metadata import write_catalog
from studies.dataset_mining.sources import seed_catalog, source_coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("artifacts/dataset_catalog.csv"))
    parser.add_argument("--source-coverage", type=Path, default=Path("artifacts/dataset_source_coverage.csv"))
    args = parser.parse_args()
    entries = seed_catalog()
    write_catalog(args.catalog, entries)
    coverage = source_coverage()
    with args.source_coverage.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage[0]))
        writer.writeheader()
        writer.writerows(coverage)
    print({"catalog_entries": len(entries), "source_coverage_entries": len(coverage)})


if __name__ == "__main__":
    main()
