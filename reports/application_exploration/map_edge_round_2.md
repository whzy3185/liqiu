# Accepted-paper map edge exploration, round 2

Date: 2026-08-25.

## Experiments

| Candidate | Runs | Decision |
|---|---:|---|
| Point-cloud adaptive compression for shape retrieval | 12 | `REJECT` |
| Grouped training-data valuation | 12 | `REJECT` |

Point-cloud GB compression loses to farthest-point sampling on retrieval and
reconstruction. Grouped valuation demonstrates a real retraining reduction, but
tree/KMeans/random grouping gives better fidelity to exact leave-one-out and
better harmful-label ranking.

## Ideas killed by collision before implementation

- Vector ANN index: GB-QkNN plus modern adaptive IVF/cluster indexes.
- Semi-supervised pseudo-label propagation: SDCG, GSFS and SCGNN.
- Lightweight image token coarsening: current GB image graphs, SegGBC, AD-GBC
  and mature token-merging methods.
- Generic industrial anomaly and fault galleries: dense current GB anomaly/fault
  literature.
- Kernel/Nystrom anchor selection: GB-USC/GB-USEC and MSRGC-Net directly use GB
  anchors for scalable manifold/graph learning.

## Current status

- `P0`: none.
- New application `P1`: none.
- Previous diagnostic purity/noise `P1`: unchanged.

## Learned search constraint

Four map-edge applications in two rounds now show the same pattern: adaptive
partitioning can be useful, but ordinary facility, KMeans, FPS, tree or random
groups obtain the same resource frontier. The next candidate must place a GB
role inside the application objective rather than use balls solely to select
representatives or batches.
