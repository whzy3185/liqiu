# Phase 2 — Audit: fixed-tree purity-frontier characterization

Branch: `oush`  
Date audited: 2026-08-31  
Phase-1 artifact: `oush_purity_frontier_theory_phase1.md`  
Status: **KILL — exact characterization reduces to a restricted standard pruning path**

## Question tested

The only permitted reformulation was whether a fixed binary tree's family of
majority-purity threshold cuts has an exact characterization that yields a
nonstandard recursive fidelity--terminal-count result. This audit compares that
object to conventional pruned subtrees with additive majority-class loss and
leaf-count cost.

## Exact characterization

Let `T` be a finite rooted binary tree with positive leaf masses and node purity
`p(v)`. Let `C` be a pruned subtree (a terminal cover of the original leaves).
Write `I(C)` for original internal nodes at which `C` continues splitting and
`L_int(C)` for terminals of `C` that were internal in the original tree. The
purity-stop rule “retain when `p(v) >= tau`; otherwise split” has the following
exact condition:

\[
C=C_\tau(T)
\quad\Longleftrightarrow\quad
\max_{v\in I(C)}p(v)<\tau\le
\min_{v\in L_{int}(C)}p(v),
\]

with an empty maximum equal to `-infinity` and an empty minimum equal to
`+infinity`. Original leaves impose no condition because they cannot split.

**Proof.** If `C=C_tau`, each split node failed the stop predicate, so its
purity is strictly below `tau`; each retained non-original leaf satisfied it,
so its purity is at least `tau`. Conversely those inequalities force exactly
the same recursive decision at every visited node. This is a local threshold
separation condition, not a new recursive phenomenon.

Two direct consequences close the proposed theorem:

1. If `tau_1 <= tau_2`, then `C_tau2` only refines `C_tau1`; the entire family
   is a nested path through the ordinary pruned-subtree space, with breakpoints
   among the finitely many node-purity values.
2. The in-tree majority fidelity is additive over terminals:

\[
\operatorname{Fid}(C)=
  \frac{1}{W(root)}\sum_{v\in C}W(v)p(v),
\qquad
\operatorname{Err}(C)=
  \frac{1}{W(root)}\sum_{v\in C}W(v)(1-p(v)).
\]

Thus the candidate asks for a leaf-count/error frontier over a **restricted
nested subfamily** of the standard pruned subtrees. A gap to the optimal
pruned-subtree frontier is only the generic fact that a restricted policy class
need not contain the optimum. It cannot supply the required GB-specific lower
bound.

## Theorem-collision matrix

| Source | Established object | Relation to `C_tau(T)` | Collision |
| --- | --- | --- | --- |
| Breiman et al., CART | A fixed tree is pruned and selected using an error/complexity trade-off. | `C_tau` is one fixed-tree pruning path; its in-tree majority error and terminal count are ordinary tree functionals. | Direct conceptual collision |
| Chou, Lookabaugh & Gray (1989) | Recursive/affine functionals over arbitrary pruned subtrees; extends CART-style pruning to tree source coding and modeling. | Additive terminal mass loss and terminal count fit the standard recursive-pruning framework. | Direct functional collision |
| Bohanec & Bratko (1994) | Finds smallest pruned decision trees satisfying an accuracy target, with dynamic programming. | The demanded fidelity-vs-terminal-count comparator is already the conventional optimization object. | Direct objective collision |
| Lin, Storer & Cohn (1992) | Finds optimal pruned tree under a leaf-count constraint; leaf-count case is polynomial. | Any claim that `N_tau` is a novel recursive complexity frontier is dominated by the full conventional pruning frontier. | Direct algorithmic collision |

## Source verification

- [CART](https://doi.org/10.1201/9781315139470) is the canonical
  fixed-tree cost-complexity/pruning source.
- [Chou, Lookabaugh & Gray (1989)](https://doi.org/10.1109/18.32124) explicitly
  reinterprets CART-style pruning for tree-structured source coding/modeling
  using recursive tree functionals.
- [Bohanec & Bratko (1994)](https://doi.org/10.1007/BF00993345) states the
  smallest-pruned-tree-with-specified-accuracy problem and its dynamic-programming
  solution.
- [Lin, Storer & Cohn (1992)](https://doi.org/10.1016/0306-4573(92)90064-7)
  studies optimal pruned trees under cost constraints and gives a polynomial
  leaf-count solution.

These sources are primary books/articles or publisher DOI records. They do not
need to name granular balls: the fixed-tree object after purity values are
assigned is exactly a conventional pruned-subtree problem.

## Gate decision

```text
Exact purity-cut correspondence: PROVED (elementary threshold separation).
Residual theorem beyond ordinary pruning: NONE IDENTIFIED.
Recursive terminal-count lower bound: restricted-policy inclusion only.
Further enumeration, proof search or empirical experiments: DO NOT RUN.
Candidate status: KILL_PURITY_CONTAMINATION_THEORY.
```

The result does not invalidate the repository's empirical observations that
purity paths may fragment under label noise. It limits their interpretation:
on a fixed tree, a scalar purity threshold is a particular nested pruning path,
not a new mathematical frontier. Any future theory must instead address the
non-additive nearest-surface routing of overlapping centre-radius balls with an
operational resource measure; that is outside this candidate and already lacks
a surviving novelty claim in the current branch.

## Integrity and boundary

- No theorem is claimed about fresh-sample generalization, adaptive KMeans tree
  construction, native boundary-distance routing, or arbitrary high-dimensional
  GBC geometry.
- No counterexample enumeration or empirical experiment was run because the
  exact correspondence already fails the Phase-1 nontriviality gate.
- This is a bounded theorem audit, not a systematic review of all tree
  combinatorics.
