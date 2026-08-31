# Phase 1 — Complexity of native nearest-surface GBC cuts

Branch: `oush`  
Status: **SCOPED — literature audit and constructive-reduction gate required**  
Date: 2026-08-31

## Narrow gap

Classical pruning results apply when a chosen terminal node has a fixed,
node-local contribution to loss. The existing clean-room GBC decision instead
predicts a query from the globally minimum terminal score

\[
D_v(x)=\lVert x-c_v\rVert-r_v.
\]

Replacing one terminal with descendants changes the candidate set and may change
the decision cells of other retained terminals. This is the only remaining
theory opening noted by the earlier collision audit. It is not an invention of a
new GB method: it analyzes the exact existing centre/mean-radius/majority-label
representation and native prediction rule.

## Primary research question

Given a fixed granular-ball hierarchy whose every node has centre, mean radius
and majority label determined by its descendant training members, a finite
labelled query set, and a terminal-ball budget, is selection of a valid tree cut
minimizing native nearest-surface classification error computationally harder
than ordinary node-additive tree pruning; and if so, can that hardness be proved
without relaxing the granular-ball construction constraints?

## FINER assessment

| Criterion | Score | Reason |
| --- | ---: | --- |
| Feasible | 2/5 | Membership-moment constraints make a valid reduction difficult; a failed construction is informative. |
| Interesting | 4/5 | Directly targets the nonlocal native routing that conventional pruning omits. |
| Novel | 2/5 | Computational-geometry/prototype-selection literature may already settle a more general problem. |
| Ethical | 5/5 | Finite formal instances only. |
| Relevant | 3/5 | A valid result would delimit when CART/TSVQ pruning baselines are applicable to GBC cuts. |
| **Average** | **3.2/5** | One kill-first proof/audit attempt only. |

## Formal decision problem

`NATIVE-GBC-CUT` input:

1. a rooted binary hierarchy `T`; every node `v` carries a finite descendant
   member multiset `S_v` consistent with the tree;
2. `c_v` equal to the arithmetic mean of `S_v`, `r_v` equal to the mean
   Euclidean distance of `S_v` to `c_v`, and `ell_v` equal to the majority
   member label with a declared deterministic tie rule;
3. a finite query set `Q={(x_i,y_i)}` disjoint from the construction members;
4. an integer terminal budget `b` and error bound `e`.

Question: is there a valid terminal cut `C` of `T` with `|C|<=b` and

\[
\sum_i 1\left[
  \ell_{\arg\min_{v\in C}(\lVert x_i-c_v\rVert-r_v)}\ne y_i
\right]\le e?
\]

Tie-breaking over equal scores must be lexicographic by immutable node id. The
decision version, rather than a post-hoc empirical Pareto frontier, is the only
object eligible for a complexity statement.

## Required proof ladder

1. **Membership in NP.** Give a polynomial certificate verifier for a proposed
   cut, including exact/rational score comparison or a declared real-arithmetic
   model. If square-root representation prevents an honest verifier statement,
   stop.
2. **Additivity contrast.** Prove by a concrete hierarchy/query witness that
   native validation loss cannot be expressed as a sum of cut-node constants.
   This witness is diagnostic only; it is not hardness.
3. **Reduction gate.** Identify a published NP-hard source problem and map every
   source instance to a hierarchy, member multisets and queries in polynomial
   size. The map must preserve each node's mean centre, mean radius and majority
   label; arbitrary free sites or radii invalidate the reduction.
4. **Comparator gate.** Show that the reduction disappears under exact
   hierarchical routing or a node-additive loss, recovering the classical
   pruning dynamic program. Otherwise it does not isolate the GB-native cause.
5. **Only after a valid reduction:** consider an exact restricted-case or
   approximation result. No theorem may be claimed from simulation alone.

## Kill conditions

Issue `KILL_NATIVE_CUT_COMPLEXITY` immediately if any applies:

- a prior source directly proves equivalent hardness/optimization for tree cuts
  under additively weighted Voronoi/ball routing;
- the only reduction uses freely chosen prototypes, radii, labels or candidate
  subsets that cannot arise from valid hierarchy members;
- the nonadditivity witness is the sole surviving result;
- the decision problem reduces to standard cost-complexity pruning once
  membership constraints are made explicit.

## Devil's-advocate checkpoint 1

### Verdict: REVISE BEFORE PHASE 2

1. **Free-prototype fallacy (critical).** A hardness result for arbitrary
   weighted Voronoi sites does not automatically apply to centres/radii that are
   tied across ancestors by sample means. The reduction must implement those
   constraints exactly.
2. **Nonadditivity-to-hardness leap (critical).** A nonadditive objective may
   still be polynomial. A counterexample to a dynamic program is not a proof of
   NP-hardness.
3. **Model-of-computation ambiguity (major).** Euclidean norms introduce square
   roots; the proof must choose rational squared-distance comparisons, a
   real-RAM statement, or an exact algebraic-number verifier.
4. **Scope inflation (minor).** This is a complexity boundary for an existing
   classifier, not an efficiency, privacy, neural-network or algorithm claim.

### Strongest counter-argument

“The problem is just a small finite model-selection search, and its global
decision cells do not make it a new computational problem.”

The only answer is a valid source-level separation and construction-respecting
reduction. Otherwise the line closes.

## Phase-2 audit protocol

Search primary sources on optimal tree cuts with nonlocal loss, hierarchical
prototype selection, additively weighted Voronoi/Apollonius classifier subset
selection, facility location with hierarchical candidates, and complexity of
nearest-site classifier editing. For each source, record whether candidates are
free or hierarchy-constrained, whether radii are free or member-derived, whether
the loss is query-global or node-additive, and whether it proves hardness or
only uses a heuristic.
