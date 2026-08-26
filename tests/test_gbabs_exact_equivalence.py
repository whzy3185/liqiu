"""Pinned-upstream equivalence tests; set GBABS_UPSTREAM_DIR to run them."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.published_methods.gbabs_exact.audit_equivalence import run_audit


@pytest.mark.parametrize("rows", [100, 500, 1000, 2000])
def test_exact_matches_pinned_upstream(rows: int) -> None:
    upstream = os.environ.get("GBABS_UPSTREAM_DIR")
    if upstream is None:
        pytest.skip("GBABS_UPSTREAM_DIR is required for upstream equivalence")
    result = run_audit(Path(upstream), Path("data/malware/raw/ember2024/elf"), rows)
    assert result["result"] == "EXACT_EQUIVALENCE_PASS", result
