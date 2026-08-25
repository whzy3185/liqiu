# Accepted-paper map edge exploration, round 1

Date: 2026-08-25.

## Map update

`granular_ball_application_map.md` records verified 2025-2026 roles including
anchor graphs, differentiable anisotropic regions, fuzzy segmentation fronts,
multi-view alignment, federated knowledge and compressed prototypes. Accepted
and published evidence is separated from arXiv-only work.

## Candidate collision screen

- Vector ANN indexing: `HIGH_COLLISION` with GB-QkNN/GBkNN, BallTree, Tribase,
  Quake and adaptive IVF partitioning.
- Semi-supervised propagation: `HIGH_COLLISION` with SDCG, GSFS and SCGNN.
- Lightweight patch/token coarsening: `HIGH_COLLISION` with GB image graphs,
  SegGBC, AD-GBC and mature token-merging methods.
- Generic industrial anomaly/fault gallery: `HIGH_COLLISION` with current GB
  anomaly and fault-diagnosis work.
- Sensor placement, compressed gallery retrieval and point-cloud compression:
  no direct accepted GB role-task collision found; generic baselines remain
  strong.

## Experiments

| Candidate | Runs | Result |
|---|---:|---|
| Spatial sensor placement/network thinning | 20 | `REJECT` |
| Fixed-slot visual/spectral gallery retrieval | 12 | `REJECT` |

Sensor placement obtains no stable error or worst-region advantage over matched
selectors. Gallery retrieval has isolated mAP signals on Satimage/Digits but no
cross-dataset transfer and materially worse rare-class coverage.

## Current P0/P1

- `P0`: none.
- New application `P1`: none after round 1.
- Previous diagnostic purity/noise `P1` remains unchanged.

## Next candidate

Point-cloud adaptive compression for shape retrieval: granular balls compress
nonuniform point density into weighted representatives. The first test must beat
random, farthest-point, voxel, KMeans and octree-like downsampling at equal point
budgets. Registration is occupied by GRICP; compression/retrieval is not yet a
direct accepted GB application.
