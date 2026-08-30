# Phase 1 — Local split / nonlocal native-routing interference

Branch: `oush`  
Status: **SCOPED — literature-audit gate not yet passed**  
Date: 2026-08-30

## Decision context

The completed adaptive-purity line is closed: its alleged GB-specific effect did
not exceed a matched CART control.  The survivor ledger leaves one untested
representation-level candidate: a split which is local in the construction tree
may alter the final native classifier away from that node, because the native
score is

\[
D_B(x)=\lVert x-c_B\rVert-r_B.
\]

This is not yet an originality claim.  Replacing one prototype by children can
change a global nearest-centre classifier too.  The study therefore tests a
narrower, falsifiable question: whether the radius-offset decision rule creates
additional, harmful changes outside the construction-local region, above that
ordinary prototype-replacement effect.

## Research Question Brief

### Primary research question

For a predesignated non-root granular-ball node, does replacing that node by its
immediate children under native boundary-distance routing alter predictions on
fresh points outside the node's construction-routing region more than the same
replacement under centre-only routing, and does the excess alteration increase
remote classification risk?

### FINER assessment

| Criterion | Score | Reason |
| --- | ---: | --- |
| Feasible | 5/5 | The existing `GranulationTree` retains centres, radii, children, split centres, and the three required synthetic geometries. |
| Interesting | 4/5 | It tests a concrete mismatch between local hierarchical construction and global terminal decision regions. |
| Novel | 2/5 | Additively weighted Voronoi/prototype-replacement theory may already explain it; no novelty is assumed before the audit. |
| Ethical | 5/5 | Public/synthetic data and CPU-only analysis; no human data or deployment. |
| Relevant | 3/5 | A positive result would constrain how GB split rules may be justified; a null result closes a tempting but weak GB direction. |
| **Average** | **3.8/5** | Advance only to a kill-first literature audit. |

### Scope boundaries

**In scope**

- The repository's maximal `GranulationTree` with its `kmeans` and
  `class_means` split generators.
- A deterministic depth-1, nonterminal node selected before any outcome is
  examined: the nonterminal child of the root with the smallest construction
  order.  Its sibling remains in the candidate set.
- Immediate replacement of that parent by its immediate children, with the
  parent and children retaining their learned majority labels, centres and mean
  radii.
- Fresh, held-out points from Gaussian blobs, moons and spirals; seeds
  `1, 7, 21, 42, 2026`.

**Out of scope**

- A new GB split, merge, radius, neural-network, privacy or encryption method.
- Root splits (there is no nonlocal construction region at the root), post-hoc
  choice of the most dramatic node, and claims about the original GBC code where
  a retained construction hierarchy is unavailable.
- Claims that any observed global change is automatically GB-specific.

**Assumptions to verify**

1. The tree's root-child assignment from `split_centers` is a reproducible,
   model-internal definition of the parent's construction-local region.
2. Centre-only replacement is an adequate ordinary-prototype control; the
   literature audit must decide whether a stronger weighted-Voronoi control is
   required.
3. The test labels are not used to select the intervened node or thresholds.

### Sub-questions

1. On what fraction of fresh points outside the selected parent's construction
   region does its replacement change the terminal identity, predicted label or
   confidence under each decision rule?
2. Does radius-offset routing produce excess remote change relative to
   centre-only routing for exactly the same parent/children and candidate set?
3. Is any excess remote change accompanied by a predeclared increase in remote
   error, rather than merely a harmless reassignment?

## Methodology blueprint

### Design

This is a controlled, paired, quantitative mechanism audit.  For every
family/generator/seed fit, form two candidate sets:

- **Before:** selected parent `P` and its root-level sibling(s).
- **After:** replace only `P` by `children(P)` while retaining the same
  sibling(s).

The construction intervention is local by definition: a point outside the
root-child region `R(P)` is still routed to the same root sibling in the
hierarchical construction rule before and after the split.  Its complement
`R(P)^c` is fixed before all native-score outcomes are calculated.

Evaluate both candidate sets with three rules:

| Rule | Score / route | Purpose |
| --- | --- | --- |
| Construction | root KMeans child, then child KMeans only inside `R(P)` | Locality oracle; remote changes must be exactly zero. |
| Centre-only | `argmin_B ||x-c_B||` | Ordinary prototype-replacement control. |
| Native GB | `argmin_B (||x-c_B||-r_B)` | The GB decision rule under test. |

This creates a necessary attribution chain:

`native remote effect` > `centre-only remote effect` > `construction remote effect = 0`.

If the centre-only control reproduces the effect, it is reported as generic
prototype replacement, not a GB finding.  If native routing does not exceed the
control, this candidate is killed even when raw native changes are nonzero.

### Frozen population and preprocessing

- Families: `gaussian_blobs`, `moons`, `spirals` from the established
  GB-core generation path.
- Generators: `kmeans`, `class_means`.
- Seeds: `1, 7, 21, 42, 2026`.
- Fit/train, validation and test draws are independent and standardized using
  train-only statistics.  The node choice uses fit data and tree order only.
- The primary population is fresh test data.  A dense two-dimensional grid is
  descriptive only for the two-dimensional geometries and cannot decide the
  gate.

This is a 3 x 2 x 5 factorial before any exclusion.  A fit with no eligible
depth-1 nonterminal node is retained as `NO_ELIGIBLE_NODE`; it is not replaced,
retuned or silently omitted.

### Frozen outcomes

For a rule `q` and remote held-out set `T_remote = {x in T : x notin R(P)}`:

\[
M_q = |T_{remote}|^{-1}\sum_{x\in T_{remote}}
  1[\operatorname{route}^{before}_q(x)\ne
    \operatorname{route}^{after}_q(x)],
\]

\[
L_q = |T_{remote}|^{-1}\sum_{x\in T_{remote}}
  1[\hat y^{after}_q(x)\ne\hat y^{before}_q(x)],
\]

\[
\Delta E_q = \operatorname{error}^{after}_q(T_{remote})-
               \operatorname{error}^{before}_q(T_{remote}).
\]

Primary estimand: `DeltaM = M_native - M_center`.  Secondary estimands are
`DeltaL = L_native - L_center` and `DeltaE = DeltaE_native - DeltaE_center`.
Route identities are mapped as `P -> P` before and `child_i -> child_i` after;
an identity change is not called a label change unless the majority label also
changes.

### Promotion / kill gates

The candidate reaches Phase 2B cheap testing only if the literature audit finds
no mechanism-equivalent prior work **and** the following predeclared empirical
gate is met:

1. Construction routing has `M_construction = 0` (within exact arithmetic) in
   every eligible fit; otherwise the local-intervention premise is invalid.
2. In every family x generator cell, at least 4/5 eligible seeds have
   `DeltaM >= 0.01` (one percentage point of fresh remote mass).
3. Across all eligible fits, the paired median `DeltaE` is at least +0.01, and
   its direction is positive in at least 20 of 30 planned fits.  This demands a
   harmful remote externality, not a geometry-only reallocation.
4. The result is not driven only by a child/parent label flip: report `DeltaM`,
   `DeltaL`, and `DeltaE` separately.  Failure of any item is **KILL** for a
   GB-specific routing-interference contribution.

These deliberately demanding gates make a null or generic result useful:
the radius-offset rule may still be documented as a decision-rule limitation,
but it cannot support a new-method or application paper.

## Devil's-advocate checkpoint 1

### Verdict: REVISE BEFORE PHASE 2

No critical flaw is present in the intervention definition, but the following
major issues must be resolved by the literature audit before experiment code is
written.

1. **Weighted-Voronoi collision risk (major).**  The score is an additively
   weighted nearest-site rule.  Its nonlocal insertion/deletion behaviour may be
   standard computational geometry, eliminating a GB-specific novelty claim.
   The audit must search that theory as the primary negative control, not merely
   GB papers.
2. **Generic prototype replacement (major).**  Any global reassignment caused
   by removing `P` can occur without radii.  The centre-only control and the
   excess estimands above are mandatory; raw `M_native > 0` is insufficient.
3. **Post-selection risk (major).**  Choosing the largest-effect split would
   manufacture a result.  The fixed depth-1/order rule and `NO_ELIGIBLE_NODE`
   retention are therefore non-negotiable.
4. **Outcome ambiguity (minor).**  Reassignment can be beneficial.  The primary
   paper-level claim is blocked unless `DeltaE` satisfies the harmful-externality
   gate; a visual decision-boundary change alone is descriptive.

### Strongest counter-argument

“This is simply the known global cell update caused by inserting/deleting sites
in an additively weighted Voronoi diagram; GB uses it as a classifier, but adds
no new mechanism.”

The only possible surviving claim is narrower: a documented mismatch between a
specific *local GB construction criterion* and its global radius-offset
decision, demonstrated after matched centre-only and construction controls.  If
the audit shows that exact mismatch has already been analyzed or repaired, the
line closes without a cheap test.

## Phase-2 literature-audit protocol (next gate, not yet executed)

Search primary sources for all of the following, with positive and negative
queries recorded:

1. `additively weighted Voronoi diagram site insertion deletion nonlocal`;
2. `Apollonius diagram nearest site radius insertion deletion classification`;
3. `granular ball classifier distance center radius decision rule split`;
4. `hierarchical prototype local split global reassignment`;
5. `granular ball adaptive split radius routing decision boundary`.

Build a mechanism-collision matrix with columns: source, candidate-set update,
decision score, locality definition, whether remote reassignment is established,
whether centre-only/weighted controls are used, remedy, and collision verdict.
Only verified primary/authoritative sources may determine the verdict.

## Reproducibility and integrity notes

- The proposed implementation is a new diagnostic only; it must not alter
  `baselines/gbc/model.py` or present itself as author code.
- No threshold may be calibrated on test outcomes.  The three numeric gates,
  seed list, family list, candidate-set definition and selected-node rule are
  frozen in this document before any results exist.
- Existing untracked `data/` and prior result files remain outside this study.
- AI assistance must be disclosed in any manuscript derived from this work.
