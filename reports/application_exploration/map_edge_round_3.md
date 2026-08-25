# Accepted-paper map edge exploration, round 3

Date: 2026-08-25.

| Candidate | Runs | Decision |
|---|---:|---|
| k-anonymous privacy microaggregation | 12 | `REJECT` |
| Fixed-region approximate deletion/unlearning | 12 | `REJECT` |

Privacy microaggregation is directly governed by group membership, but MDAV and
merged KMeans preserve more utility at the same k. Fixed-region deletion can be
much faster than rebuilding, but KMeans/tree regions preserve the rebuilt model
more reliably.

Neither result should be generalized beyond its contract: microaggregation is
not differential privacy, and local statistic updates are not certified machine
unlearning.

## Current status

- `P0`: none.
- New application `P1`: none.
- Previous diagnostic purity/noise `P1`: unchanged.

## Next map search

Representative selection, batching, spatial coverage, point compression,
grouped retraining, privacy cells and local deletion have all failed matched
non-GB controls. Continue only with roles where balls carry learned semantics,
uncertainty or interactions inside the objective, following AD-GBC, SegGBC,
HOARD/GFSAF and FedOC-GB rather than classical recursive clustering alone.
