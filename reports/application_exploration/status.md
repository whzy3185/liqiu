# Granular-ball application exploration status

Updated: 2026-08-25.

## ACTIVE CANDIDATES

| Candidate | Status | Next cheap test |
|---|---|---|
| Batch active learning | `P1-low` | five small classification datasets; same-partition KMeans/coreset gate |

## P0

None.

## P1

No application is currently P1 after the first three kill tests.

## REJECTED

- Fixed-memory GB drift sketch: KMeans beats it at identical bytes in all four
  shift families; only 2/20 runs clear the +2 pp equal-memory gate.
- Contextual cell-error cleaning: zero of 15 runs beat the strongest matched
  baseline by 3 pp AUPRC, and radius routing loses to the same-tree center-only
  ablation. Robust local statistics, not GB geometry, explain the useful signal.
- Hard-budget local regranulation: only 5/9 runs meet the 1 pp risk gate, 3/9 meet
  the update-time gate, and 0/9 show a 1 pp radius advantage over center-only.
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

1. Run one matched batch-active-learning kill test. Query selection must use no
   unseen labels and compare entropy, k-center and matched-K KMeans batches.
2. Require label-budget Accuracy AUC improvement of at least .5 pp in at least
   three datasets and a same-partition/radius attribution signal.
3. If rejected, pause this exploration tranche: every remaining nearby role is
   either directly occupied or has failed a matched non-GB baseline.
