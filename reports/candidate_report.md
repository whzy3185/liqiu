# Candidate report

Intentionally empty until experimentally supported failure patterns exist.

## Cheap Test ledger

### M01 — rejected

One-sided Wilson lower-bound purity stopping was tested on five public datasets
and three seeds. It improves Banknote/Sonar but exacerbates Electricity granule
explosion and Ionosphere over-refinement. Because it also collides with generic
small-sample tree-pruning principles, it is removed from the implementation queue.

### M02 — v1 invalid; corrected v2 pending

The first 45-run global validation control double-scaled the test set after
refitting preprocessing. All `m02gv1-*` records are retained as pipeline failures
and excluded from evidence. M02 priority is unchanged until `m02gv2-*` completes.
