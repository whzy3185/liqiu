# Granular-ball application exploration status

Updated: 2026-08-25.

## ACTIVE CANDIDATES

| Candidate | Status | Next cheap test |
|---|---|---|
| Contextual cell-error cleaning | `P1` | 3 numeric tables x 4 cell corruptions x 5 seeds; matched local baselines |
| Hard-budget local regranulation | `P1` | concept/covariate/emerging streams; fixed bytes and update-time gate |
| Batch active learning | `P1-low` | defer until the first two candidates are killed or promoted |

## P0

None.

## P1

- Contextual cell-error cleaning: application gap is cell-level corruption, not
  row anomaly or label noise. Direct GB cell-repair work was not found in the
  2024-2026 scan, but generic conformal cleaning and contextual tabular anomaly
  methods are strong collisions.
- Hard-budget local regranulation: the repository's sliding GBC rebuild is much
  slower and less accurate than online SGD on concept drift. A local update can
  continue only if it matches risk within 1 pp at less than 20% of rebuild time.

## REJECTED

- Fixed-memory GB drift sketch: KMeans beats it at identical bytes in all four
  shift families; only 2/20 runs clear the +2 pp equal-memory gate.
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

1. Run contextual cell-error cleaning without target labels or corruption-mask
   leakage. Compare global robust scores, kNN context, matched-k KMeans context,
   and a supervised per-column predictor.
2. Kill unless GB improves cell AUPRC by at least .03 over the strongest cheap
   baseline on at least three datasets, or improves clean-test downstream score
   by at least .5 pp at the same review budget.
3. If rejected, move to the nine-run hard-budget local regranulation test. Do not
   return to anomaly, replay, federated or open-world memory directions.
