# Granular-ball application exploration status

Updated: 2026-08-25.

## ACTIVE CANDIDATES

| Candidate | Status | Next cheap test |
|---|---|---|
| Hard-budget local regranulation | `P1` | concept/covariate/emerging streams; fixed bytes and update-time gate |
| Batch active learning | `P1-low` | defer until the first two candidates are killed or promoted |

## P0

None.

## P1

- Hard-budget local regranulation: the repository's sliding GBC rebuild is much
  slower and less accurate than online SGD on concept drift. A local update can
  continue only if it matches risk within 1 pp at less than 20% of rebuild time.

## REJECTED

- Fixed-memory GB drift sketch: KMeans beats it at identical bytes in all four
  shift families; only 2/20 runs clear the +2 pp equal-memory gate.
- Contextual cell-error cleaning: zero of 15 runs beat the strongest matched
  baseline by 3 pp AUPRC, and radius routing loses to the same-tree center-only
  ablation. Robust local statistics, not GB geometry, explain the useful signal.
- Generic GB anomaly detection and time-series anomaly detection: directly
  occupied by multiple 2025-2026 methods, including AAAI 2026 GBOC/GVDD.
- GB replay/prototype continual memory: BallIL, EG-CNN and strong non-GB compact
  replay methods directly occupy the role.
- Federated GB knowledge cache and open-world GB memory: direct recent GB work
  and the repository's own negative equal-byte federated result close them.

## UNEXPLORED APPLICATIONS

- Cell-level tabular repair under heterogeneous local correlations.
- Multi-annotator local competence and re-annotation allocation.
- Batch active learning under rare local modes.
- Local update scheduling after a hard-budget GB state is shown viable.

## NEXT CHEAP TESTS

1. Run the nine-cell hard-budget local regranulation test on concept, covariate
   and emerging-class streams.
2. Require risk within 1 pp of the best existing stream baseline, update time at
   most 20% of sliding rebuild, and a fixed ball/byte cap in at least two shifts.
3. If rejected, move to batch active learning. Do not return to anomaly, replay,
   federated, open-world memory, generic drift sketches or cell cleaning.
