# Phase 1 — Fixed-tree purity-frontier characterization

Branch: `oush`  
Status: **SCOPED — one permitted reformulation; literature gate required**  
Date: 2026-08-31

## What is already closed

The following cannot be claimed as a paper contribution:

- sensitivity of purity to label noise;
- a global threshold being inferior to regional choices;
- a marked-leaf / ancestor-union count bound for a binary tree;
- an optimizer over global or regional purity thresholds.

Those statements collide with noisy-label GB work, cost-complexity pruning,
adaptive partitions and standard tree combinatorics. The current empirical
global-frontier results remain only a `P1_APPLICATION_EXPLANATION` because their
region routing is given and their oracle evaluates hidden test risk.

## Primary research question

For a fixed finite binary hierarchy with leaf labels and purity defined by the
maximum class proportion in a node, can the complete family of threshold cuts be
characterized exactly as a constrained family of terminal subtrees, and does
that characterization imply a nontrivial recursive lower bound on the number of
terminal balls required to attain a specified training fidelity under an
adversarial but bounded label-contamination pattern?

The question deliberately concerns a fixed hierarchy. It makes no claim about
the data-dependent KMeans construction, generalization, optimal pruning, or a
new GBC split rule.

## FINER assessment

| Criterion | Score | Reason |
| --- | ---: | --- |
| Feasible | 3/5 | Finite-tree definitions and counterexample search are local; a nontrivial theorem may nevertheless fail. |
| Interesting | 3/5 | It isolates the recursive stop rule rather than another threshold heuristic. |
| Novel | 2/5 | Standard pruning and marked-subtree theory are close; novelty survives only if the exact purity-frontier statement is not a renaming. |
| Ethical | 5/5 | Formal/synthetic analysis only. |
| Relevant | 3/5 | A theorem could give a rigorous boundary for purity-based GB claims; a null result cleanly ends the theory line. |
| **Average** | **3.2/5** | One literature-gated proof attempt only. |

## Formal object

Let `T` be a rooted finite binary tree. Each leaf `ell` has a class label in
`{1,...,K}` and a positive mass `w(ell)`; each internal node represents the
union of descendant leaves. For any node `v`, let

\[
p(v)=\max_k \frac{\sum_{\ell\preceq v}w(\ell)1[y(\ell)=k]}
                       {\sum_{\ell\preceq v}w(\ell)}.
\]

The purity cut `C_tau(T)` visits the root and retains `v` iff `p(v) >= tau` or
`v` is a leaf; otherwise it recurses to both children. Its structural cost is
`N_tau=|C_tau(T)|`. For any retained node, the prediction is its majority class;
the induced in-tree fidelity is the mass-weighted majority accuracy over the
cut.

The allowed statement must characterize the set

\[
\mathcal{F}(T)=\{(N_\tau,\operatorname{Fid}(C_\tau(T))):\tau\in[1/K,1]\}
\]

in relation to terminal subtrees whose nodes are not necessarily all
monochromatic. A theorem that simply says corrupted leaves force their ancestor
union to be split is classified as standard and does not survive.

## Required theorem ladder

1. **Exact correspondence lemma.** State and prove or disprove whether every
   purity threshold cut is a monotone terminal-subtree family with identifiable
   breakpoints at node purities, and conversely which terminal subtrees are
   representable by one scalar threshold.
2. **Nontriviality test.** Reduce the correspondence to a complete balanced tree
   with unit weights and compare it explicitly to the standard marked-leaf
   ancestor-union bound. If the result is equivalent under a relabeling, issue
   `KILL_PURITY_CONTAMINATION_THEORY`.
3. **Only if step 2 survives:** construct a bounded-contamination family where
   every scalar threshold meeting a specified fidelity must include a strictly
   larger recursive terminal cost than a stated comparator class. The comparator
   must be an optimal conventional subtree/pruning frontier, not an oracle
   regional threshold menu.
4. **Only if step 3 survives:** separate in-tree fidelity from fresh-sample risk
   and state no generalization claim without an independently proven sampling
   argument.

Failure at any step stops the ladder. No empirical sweep, neural method,
threshold repair or new GBC generator is authorized by this plan.

## Proof and counterexample protocol

- Enumerate all labelled binary trees up to a predeclared small leaf limit for
  counterexamples to the proposed correspondence; use rational weights only.
- Treat the enumeration as a proof debugger, never as a theorem proof.
- For every proposed lower bound, write the exact contamination budget, tree
  topology, class count, threshold interval, fidelity target and comparator.
- Use no test-data oracle or selected synthetic family as mathematical evidence.
- Retain negative counterexamples and failed lemmas in the proof log.

## Devil's-advocate checkpoint 1

### Verdict: REVISE BEFORE PHASE 2

1. **Renamed combinatorics (critical).** The likely outcome is an old
   marked-subtree statement. Exact reduction to that object is a KILL, not a
   partial success.
2. **Wrong comparator (critical).** Showing a scalar threshold loses to an
   arbitrary nonuniform cut is policy-class inclusion, not a lower bound. The
   comparator must include optimal conventional pruning.
3. **Training-risk overreach (major).** Node purity and in-tree fidelity do not
   prove fresh risk or robustness. Any population claim needs separate
   assumptions and proof.
4. **Relevance drift (minor).** This line is a theory/negative-boundary study,
   not the neural/application route originally desired; it is pursued only
   because all currently auditable application routes are closed.

### Strongest counter-argument

“A scalar threshold produces nested tree cuts, so any claimed terminal-count
phenomenon is just ordinary pruning or trie combinatorics.”

The proof attempt must defeat that statement with an exact residual property.
If it cannot, the correct conclusion is a documented equivalence and KILL.

## Phase-2 literature-audit protocol

Search primary sources on: purity-based decision-tree pruning; impurity/purity
threshold cuts; monochromatic subtree covers; marked-leaf ancestor unions;
optimal tree pruning under leaf/error constraints; and robust hierarchical
partition lower bounds. Build a theorem-collision matrix containing assumptions,
tree object, cut family, cost, fidelity/loss, stated bound and exact relation to
`C_tau(T)`. The audit must use a source-level theorem comparison, not title
similarity.
