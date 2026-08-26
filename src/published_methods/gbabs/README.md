# GBABS Upstream Provenance

Method: *Approximate Borderline Sampling Using Granular-Ball for Classification
Tasks*, IEEE ICDE 2025, DOI `10.1109/ICDE65448.2025.00295`.

Official source: <https://github.com/CherylTse/GBABS>, pinned at
`081e9df97f946dc8c2adbf5622fe421e2412da02` on 2026-08-26.

The source is fetched at that exact revision into an ignored execution cache.
The runner imports `GBABS.py` and `RD_GBG.py` unchanged. No mathematical or
sampling-rule modification is permitted. The local wrapper provides provenance,
train-only scaling already used by upstream `main.py`, seed logging, and timing.

On EMBER2024 ELF, an upstream preflight at 2,000 labeled training rows consumed
8.9 GB maximum resident memory and 26.9 seconds. A complete 23,792-row run was
terminated by the operating system (`RC 137`); thus GBABS is recorded as
`COMPUTE_LIMIT` rather than approximated, retuned, or replaced.
