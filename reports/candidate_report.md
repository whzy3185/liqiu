# Candidate report

Intentionally empty until experimentally supported failure patterns exist.

## Cheap Test ledger

### M01 — rejected

One-sided Wilson lower-bound purity stopping was tested on five public datasets
and three seeds. It improves Banknote/Sonar but exacerbates Electricity granule
explosion and Ionosphere over-refinement. Because it also collides with generic
small-sample tree-pruning principles, it is removed from the implementation queue.

### M02 — mixed, lower priority

The first 45-run control (`m02gv1-*`) double-scaled test data and is invalid.
Corrected `m02gv2-*` improves Banknote and Phoneme and finds a lower-cost
Electricity setting, but catastrophically over-selects purity on one Ionosphere
seed and slightly harms Sonar. M02 survives only as a local, resampling-stable
risk/cost mechanism; ordinary single-split validation is an inadequate solution.

### M04 — not viable as a single-objective mechanism

The 45-run global Brier/ball-cost control produces strong Brier and efficiency
gains on Electricity but loses about 0.048 Accuracy, helps Banknote/Phoneme, and
is unstable or harmful on Ionosphere/Sonar. Calibration is a necessary outcome
constraint, not a standalone split objective. M04 is removed from the leading
queue and may only participate in a multi-objective mechanism.

### M12 — rejected

Knee, discrete-curvature and 1%-plateau rules were compared under nested
validation. Their selected purity and held-out behavior disagree sharply; each
has a catastrophic dataset/seed. M12 lacks a non-arbitrary statistical decision
property and is removed from the candidate queue.

### M02 local stable pruning — rejected

A three-fold cross-fit local keep/split prototype reduced thousands of leaves to
tens, but consistently lost Accuracy on Electricity and Phoneme. A bounded
min-validation sensitivity check (5/10/20) did not rescue it. Sparse local
validation is a structural limitation, not a tunable implementation detail.

### Candidate 2 / M08 sequential control — not retained

A paired empirical-Bernstein three-way controller evaluated purity alternatives
in batches and could ACCEPT, REJECT or INVESTIGATE. Across 30 runs and two δ
levels it consumed every validation sample, accepted no alternative, and always
fell back to p=.85. It is safe but provides no adaptation or VOI savings. Less
conservative variants lose the claimed distribution-free protection; the result
is redirected to Candidate 6 sample-complexity analysis.

### Candidate 3 / M14 boundary metrics — failed decisive test

Five predeclared structure/mixing metrics were tested across 90 runs. Their
leave-case-out prediction is worse than a constant baseline. Candidate 3 is
demoted to P2; M14 is rejected. A future attempt must introduce independently
motivated curvature/scale/topology statistics and clear the boundary-aware
MDL-GBC collision.
