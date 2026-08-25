# Granular-ball application exploration status

Updated: 2026-08-25.

## ACTIVE CANDIDATES

| Candidate | Status | Next cheap test |
|---|---|---|
No active candidate survives this tranche.

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
- Batch active learning: only 4/25 runs beat the strongest selector by .5 pp;
  radius weighting loses to the same partition without radius on average.
- Local annotator competence: oracle-local results confirm a real regional
  competence opportunity, but full GB loses to kNN/tree/KMeans/terminal variants;
  0/45 competence and allocation cells pass the strongest-baseline gates, and
  same-partition radius attribution is absent.
- Spatial sensor placement: 0/20 runs pass the joint +5% mean/worst-region RMSE
  gate. KMeans, k-center, facility-location or axis selection explains the useful
  station coverage.
- Fixed-slot gallery retrieval: only 1/12 runs passes +2 pp mAP and none passes
  mAP plus rare-class Hit jointly. All compressed methods receive the same 90%
  distance-computation reduction.
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

Pause this exploration tranche. Four new application roles failed matched
non-GB or same-partition attribution gates, while anomaly detection, time-series
anomaly, replay/continual memory, federated cache and open-world memory are
directly occupied by recent granular-ball work. Reopening requires a new
application pain point or a materially different GB role, not another score or
downstream model.

The targeted crowd-annotation reopening is also closed. A future cycle may keep
the *problem* of local annotator competence, but it must introduce a materially
different region/membership mechanism and first beat the exact same hierarchy
without radius. The current GB local-reliability mechanism must not be tuned or
expanded to real crowd data.

The accepted-paper map is now the search driver. Vector ANN indexing,
semi-supervised propagation and lightweight image token coarsening were rejected
at collision search. Point-cloud adaptive compression/retrieval is the next
`CLEAR_DIRECT_GB / PARTIAL_GENERIC` Cheap Candidate.
