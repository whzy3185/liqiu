# A3 Current-State Audit

## Repository state

- Current branch: `exp/granular-ball-privacy-refinement`.
- Current commit: `c3f23c5ac358f1ff9b69d5f0b875b3cb2d02569a`.
- Reference commit `c3f23c5` is the current HEAD, so no later A3 work needed
  migration or reconciliation.
- The local untracked `data/` directory predates this phase and is preserved
  outside the branch's tracked research artifacts.

## Existing A3 work

The branch contains a purity-cut `GranulationTree`, GB releases at thresholds
0.70--0.99, Release 1/2/3 information budgets, and matched-k KMeans releases.
Raw ball/member trajectories, synthetic discovery grids, held-out synthetic
confirmation, natural real-data tests, semi-synthetic label-noise interventions,
and group-disjoint Musk1 tests are all retained.

Synthetic confirmation found a positive GB-minus-KMeans AUC contrast in a
high-dimensional, low-redundancy, locally heterogeneous, noisy mixture regime.
Real transfer has not been confirmed: Sonar, Spambase, Digits, and group-split
Musk1 are zero or negative relative to matched KMeans.

## Existing attack protocol

`studies/privacy_refinement/a3.py::attack_metrics` builds a release from one
member set, concatenates that same release's members and non-members as attack
candidates, then uses candidate-level `StratifiedKFold` cross-validation. It
uses Logistic Regression and Random Forest on release-derived geometric
features. This establishes same-release membership separability, but the attack
fit sees folds from the same release as the target candidates.

## Existing controls and mechanism evidence

- Matched-k KMeans controls number of groups under the same train split.
- Release 1/2/3 separate disclosure budgets.
- Natural, semi-synthetic, and group-disjoint tests distinguish evidentiary
  levels.
- Small-ball analysis finds high attack AUC in tiny regions for both GB and
  KMeans; the GB excess is suggestive but has limited matched-bin support.

## Missing methodological controls

1. No shadow-release-to-independent-target-release attack exists.
2. No attack model is trained exclusively on shadow releases and evaluated on
   disjoint target pools.
3. Synthetic label noise is generated before the current member split, rather
   than held fixed while membership changes across releases.
4. No explicit audit documents whether every preprocessing transform is fit
   only on construction members or on an external reference.
5. The prior synthetic confirmation therefore cannot yet be labeled a standard
   membership-inference result.

## B0 status

`KILL_B`. The GBFRS feature-selection output audit is complete and remains
closed.

## Next unresolved question

Does the frozen synthetic GB-minus-KMeans contrast remain under a strict
cross-release attack where shadow and target candidate pools have no shared
samples, target membership labels never train the attacker, and fixed noisy
labels are independent of member selection? This is the highest-priority gate
before any metadata-first dataset mining or new real-data A3 experiment.
