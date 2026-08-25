# Accepted-paper map edge exploration, round 5

Date: 2026-08-25.

| Candidate | Runs | Decision |
|---|---:|---|
| Learnable anisotropic GB for missing-view recovery | 12 | `REJECT` |

This round deliberately changed mechanism class from fixed recursive regions to
learnable centers/scales/prototypes on MPS. The result remains negative: MLP and
Ridge recover missing views more accurately and give higher downstream utility.

## Continuous-search state

The accepted-paper map now covers clustering, graph coarsening/pooling,
segmentation, anomaly, open intent, weak supervision, recommendation, regression,
optimization and explanation. Collision search closes vector ANN,
semi-supervised propagation, lightweight token coarsening and generic industrial
anomaly before implementation.

Ten new map-edge application candidates have been experimentally closed across
five pushed tranches. The remaining credible expansion route is no longer a
Cheap Test with classical partitions: it requires reproducing a modern accepted
learnable module (AD-GBC/SegGBC/GFSAF/HOARD) and transferring it to a specific
real dense-prediction or multimodal benchmark. That requires a human choice of
target benchmark, data license/download and formal MPS/GPU budget.

## Current P0/P1

- `P0`: none.
- New application `P1`: none.
- Previous diagnostic purity/noise `P1`: unchanged.
