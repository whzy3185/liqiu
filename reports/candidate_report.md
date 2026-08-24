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
