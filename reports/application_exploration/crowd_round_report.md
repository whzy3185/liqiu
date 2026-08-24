# Local annotator competence exploration round

Date: 2026-08-25.

## Explored

- Searched direct GB crowd/multi-annotator/local-competence work and audited
  NUTMEG, Crowd-Kit, CROWDLAB/ActiveLab and five classic crowd datasets.
- Implemented global Dawid-Skene plus matched GB, KMeans, kNN and tree local
  competence estimators.
- Executed 60/60 successful CPU configurations: three datasets, three hidden
  local competence geometries, five seeds, and 15 global-only controls.
- Evaluated truth aggregation, unqueryable competence probes, calibration,
  capacity-limited additional-label allocation, worst-region accuracy and a
  fixed downstream classifier.

## Failure and opportunity

The opportunity is real: oracle-local competence often improves aggregation by
4-9 percentage points over global Dawid-Skene. The tested GB mechanism does not
recover it.

- Full GB competence AUPRC trails the best non-oracle local baseline by 2.37 pp
  on average; gate pass count is 0/45.
- Capacity-limited allocation AUC trails the best baseline by 4.35 pp; gate pass
  count is 0/45.
- Same-tree radius attribution is effectively zero for competence and negative
  for allocation.
- kNN is most frequently strongest for allocation; tree, KMeans and terminal
  hierarchy variants also win cells.

## Killed

`Granular-Ball Local Annotator Competence / Re-annotation Allocation` is
`REJECT` for the tested mechanism. Do not tune radius, hierarchy depth,
shrinkage, region count or allocation score, and do not expand it to real crowd
datasets.

The broader problem of feature-local annotator competence remains interesting,
but it is not an active GB candidate unless a new mechanism explains why ball
coverage/membership should beat the identical hierarchy with centers only.

## Current P0

None.

## Current P1

No new application P1. The previous purity/noise risk-resource failure remains
the only diagnostic P1 in the repository.

## Strongest three signals

1. `P1`: purity/noise fragmentation and clean-risk reversal; stable but highly
   collided and without a repair.
2. `REJECT`: local annotator competence; real oracle gap, failed GB estimator and
   attribution.
3. `REJECT`: generic hard-budget online prototypes; useful systems behavior,
   but center-only explains it.

## Next search constraint

Do not return to generic application scanning. A future candidate must make a
ball property operational before implementation: coverage, overlap, containment,
region membership or multiple supervision sources must enter the task objective
itself. The first kill test must include the identical partition with radius and
membership removed.
