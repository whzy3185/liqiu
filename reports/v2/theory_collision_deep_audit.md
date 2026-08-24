# V2 theory collision deep audit

Audit date: 2026-08-24

Audited claim: a known-region, nonuniform cut of maximal granular-ball trees
allocates a finite granule budget to the regions where refinement has the most
task value, and can strictly improve on one global purity threshold.

## Executive verdict

**Standalone novelty status: `HIGH_COLLISION / NOT_YET_NOVEL`.**

The current optimization is not a new theory of resource-aware granularity. At
the level of its finite optimization problem, it is constrained model selection
over a product of regional pruning paths. Its closest antecedents are stronger
than generic structural risk minimization:

1. CART already prunes a fixed large tree by trading empirical error against
   leaf count.
2. Chou, Lookabaugh, and Gray (1989) explicitly reinterpret CART pruning as an
   operational distortion-rate problem, including tree-structured vector
   quantization, minimum expected-cost decision trees, optimum bit allocation,
   and minimum-leaf criteria.
3. Bohanec and Bratko (1994) pose almost the literal constrained objective:
   find the smallest pruned tree that remains within a specified accuracy.
4. Lin, Storer, and Cohn (1992) optimize a pruned tree-structured vector
   quantizer under a leaf-count constraint in polynomial time.
5. Adaptive partition theory already studies putting more cells where the
   response is irregular, while spatially adaptive decision-tree penalties
   already depend on sample location and tree shape.

There is one real mathematical difference that must not be erased: the present
granular-ball predictor routes a query by global nearest surface distance
`||x-center|| - radius`, not by following a root-to-leaf decision path. Loss is
therefore not generally additive over granular-ball nodes, so the usual CART
nodewise dynamic program is not automatically an algorithm for arbitrary
granular-ball cuts. The current experiment, however, does not solve that harder
problem. It precomputes only ten whole-cut candidates per known region and
exhaustively selects among their Cartesian product. That is ordinary finite
resource allocation/model selection.

The defensible current status remains `P1_APPLICATION_EXPLANATION`. A P0 theory
claim would require a granular-ball-specific result about the nonadditive,
overlapping center-radius geometry, unknown routing, or a real byte/time budget,
and it must beat optimal-pruning and adaptive-partition baselines.

## 1. Exact object audited from the repository

This audit treats the implementation, not the intended prose, as authoritative.
The relevant code is `studies/risk_granularity/tree.py` and
`studies/risk_granularity/theory_harness.py`.

For each observed region `r`:

- a separate maximal binary granulation tree `T_r` is fit on the training
  samples carrying that region label;
- the tree is grown by KMeans or class-mean-seeded KMeans until purity 1,
  `min_samples`, or `max_depth` stops it;
- each threshold in
  `Theta = {.55, .60, .65, .70, .75, .80, .85, .90, .95, 1.0}` yields one
  nested cut `S_{r,k}`;
- its resource is the number of selected nodes/leaves `c_{r,k}`;
- its validation error count is `e^v_{r,k}` and its test error count is
  `e^t_{r,k}`.

For a choice vector `k = (k_1,...,k_m)`, the implemented quantities are

```text
C(k)       = sum_r c_{r,k_r}
R_val(k)   = (sum_r e^v_{r,k_r}) / (sum_r n^v_r)
R_test(k)  = (sum_r e^t_{r,k_r}) / (sum_r n^t_r).
```

The two policy classes are

```text
G_global     = {(k,...,k): k in {1,...,10}}
G_nonuniform = {1,...,10}^m.
```

The deployable-looking G3 selector is

```text
minimize    C(k)
subject to  R_val(k) <= R_val(k_full) + epsilon,
```

with ties broken by validation risk. Here `k_full` is threshold 1.0 and thus
selects terminal nodes of the already grown tree. The reported oracle frontier
instead Pareto-filters all choices using `R_test`; it is explicitly an
existence diagnostic and is not a valid deployable selector.

Two implementation facts materially constrain the claim:

1. **Region routing is given.** The procedure trains, validates, and predicts
   separately after filtering on the synthetic region identifier. Without an
   observed routing variable, it is not yet a classifier for a new unlabeled
   point.
2. **A granular cut is not a conventional decision-tree partition.** Prediction
   selects, among all nodes in a cut, the smallest
   `||x-center_j|| - radius_j`. These induced cells are weighted Voronoi-like
   regions and can cross the clustering tree's ancestral boundaries. Standard
   additive leaf-error pruning does not directly describe this predictor.

The implemented memory value `(dimension + 3) * 8 * granule_count` is only a
proxy. Tree pointers, class-count representation, allocator overhead, routing,
and query-time comparisons are not measured. Runtime and memory are recorded,
but neither is the optimized resource.

## 2. Mathematical normal form and the non-novel core

### 2.1 The current regional selection is a multiple-choice allocation problem

Once the ten candidate cuts per region have been evaluated, tree geometry has
left the optimizer. It sees `m` finite lists of `(cost, error)` pairs and chooses
one pair from each list under an additive constraint. With integer validation
errors this is a multiple-choice knapsack/Pareto-frontier problem. The current
code uses `10^m` exhaustive enumeration; dynamic programming or Lagrangian
selection would be standard alternatives.

For any multiplier `lambda >= 0`, define the regional score

```text
j_{r,k} = w_r R_{r,k} + lambda c_{r,k},
```

where `w_r = n_r / sum_s n_s`. Then the nonuniform penalized optimum separates:

```text
min_{k_1,...,k_m} sum_r j_{r,k_r} = sum_r min_k j_{r,k}.
```

The global-threshold optimum is

```text
min_k sum_r j_{r,k}.
```

Consequently the exact price of uniformity is

```text
Delta_global
  = min_k sum_r j_{r,k} - sum_r min_k j_{r,k}
  = min_k sum_r (j_{r,k} - min_l j_{r,l}) >= 0.
```

It is strictly positive exactly when there is no common threshold that is
simultaneously region-optimal, after accounting for ties. This identity needs
no property of granular balls. It applies unchanged to image blocks, clients,
subgraphs, quantizers, experts, or any collection of regional model menus.

The Lagrangian recovers supported points of the discrete constrained frontier.
Unsupported points on a nonconvex frontier may not be optimal for any single
`lambda`, so constrained and penalized forms are not universally one-to-one.
That familiar discrete-optimization detail does not create a new granularity
theory.

### 2.2 What the empirical positive regret does and does not prove

Because `G_global` is a strict subset of `G_nonuniform`, nonnegative oracle
regret follows from policy-class inclusion. Positive regret is useful evidence
that the larger class is not vacuous on the generated distributions, but it is
not by itself a surprising theorem.

Moreover, the oracle frontier and the global regret are both constructed from
the same test sample. Searching up to `10^m` choices on test outcomes creates an
optimistic oracle and a multiple-comparisons effect. This is acceptable for a
labeled diagnostic, but a theoretical or method claim needs analytic population
risk, a very large independent Monte Carlo evaluation set, or a second untouched
confirmation set after freezing the oracle policy class.

## 3. Ranked closest works

| Rank | Work | Direct collision | Residual difference | Collision |
|---:|---|---|---|---|
| 1 | Chou, Lookabaugh & Gray (1989) | Prunes a fixed tree along an operational distortion-rate frontier; explicitly covers TSVQ, error/cost trees, bit allocation, and minimum leaves | Uses source-code/tree routing and additive tree functionals, not nearest-surface granular-ball prediction | **Very high** |
| 2 | Bohanec & Bratko (1994) | Finds the smallest pruned tree within specified accuracy and the most accurate tree at each size by dynamic programming | Conventional decision-tree semantics and a richer set of pruned subtrees | **Very high** |
| 3 | Breiman et al., CART (1984) | Fixed maximal tree, leaf-count complexity, error-complexity frontier, validation/cross-validation selection | CART has feature-test routing and additive leaf loss | **Very high** |
| 4 | Lin, Storer & Cohn (1992) | Optimal fixed-tree VQ pruning under leaf-count constraint; `O(nk)` algorithm for a leaf budget | Distortion and tree-quantizer routing differ from current task loss and routing | **Very high** |
| 5 | Scott & Nowak (2006) | Penalized ERM over adaptive dyadic trees with a spatially adaptive penalty depending on samples and tree shape, plus oracle inequalities and near-minimax rates | Axis-aligned dyadic cells, not learned center-radius balls | **High** |
| 6 | Nobel (1996) | Data-dependent partitions can allocate more cells in clusters or where responses are erratic; gives consistency conditions | Regression/histogram cells and asymptotics, no present GBC routing | **High conceptually** |
| 7 | SRM/model-selection literature | Selects among data-dependent model hierarchies using risk-complexity control | Current validation constraint has no generalization penalty or bound | **High at formulation level** |
| 8 | Shannon rate-distortion; classification-aware quantization | Minimum representational rate at tolerated distortion; task loss can be the distortion | Current leaf count is not bit rate or mutual information | **Medium in Shannon form; very high through TSVQ pruning** |
| 9 | Hart prototype condensation and modern coresets | Reduce retained representatives while preserving prediction or optimization behavior | Current balls are weighted summaries, not necessarily data points or uniform objective approximations | **Medium** |

## 4. Forced comparison by literature family

### 4.1 CART cost-complexity pruning

For a subtree `S` of a large tree, CART studies an objective of the form

```text
R_alpha(S) = R_hat(S) + alpha |leaves(S)|.
```

Minimal cost-complexity pruning produces a nested sequence of optimal subtrees,
then an independent estimate or cross-validation chooses tree size. The 1984
book's dedicated chapters on minimal cost-complexity and optimal pruning are the
canonical source; the current publisher edition is linked in the source
register.

**Mathematical equivalence.** If the known regions are represented as fixed top
branches, resource is leaf count, and each leaf has path-local additive loss,
then the proposed risk-resource objective is CART's pruning problem in
constrained rather than penalized form. Region-specific refinement is simply an
unbalanced subtree.

**Material difference.** In this repository, region routing is external and a
cut predicts by comparing every retained ball. The validation loss of an
arbitrary cut is not a sum of immutable node losses because adding one ball can
change Voronoi-like decision regions belonging to other balls. CART's
weakest-link theorem therefore cannot be imported without new assumptions.
Nevertheless, the current ten-threshold product search avoids, rather than
solves, this issue.

**Potential Reviewer Objection.** "This is cost-complexity pruning applied to a
forest whose leaves are called granular balls. Why is a global purity threshold
the only baseline, instead of the standard optimal subtree frontier?"

**Audit finding.** Fatal to a generic standalone claim. Not fatal only to a
future theorem that explicitly exploits and analyzes the nonadditive
center-radius routing.

### 4.2 Optimal pruning and tree-structured vector quantization

Three sources make this collision more direct than CART alone.

- Chou, Lookabaugh, and Gray (1989) state that the BFOS/CART algorithm starts
  with a large tree and prunes it to the fewest leaves for a given probability
  of error. They extend it to an operational distortion-rate frontier for
  tree-structured source coding and modeling, including minimum leaf count and
  optimum bit allocation.
- Bohanec and Bratko (1994) ask for the smallest pruned decision tree that
  represents a concept within specified accuracy and use dynamic programming to
  generate the best accuracy available at each tree size.
- Lin, Storer, and Cohn (1992) define optimal TSVQ pruning under a cost
  constraint. They show that the leaf-count-constrained case is polynomial and
  give an `O(nk)` algorithm, while some other costs such as entropy or expected
  depth are NP-hard.

**Mathematical equivalence.** "Minimize granules subject to risk within
`epsilon`" has the same bi-criterion form as "minimize leaves/rate subject to
error/distortion." Under a fixed tree and a leaf-count cost, changing the name
of a code cell or tree leaf to a granule supplies no novelty.

**Material difference.** The current candidate family is much narrower than
all subtrees: it includes only cuts induced by ten scalar purity thresholds in
each regional tree. Conversely, its nearest-surface prediction can make the
arbitrary-cut objective nonadditive. These differences mean the old algorithms
are not drop-in implementations, but they make the present exhaustive algorithm
less, not more, theoretically substantial.

**Potential Reviewer Objection.** "The 1989 TSVQ paper already unifies pruning,
rate-distortion, minimum expected cost, and bit allocation. What theorem here is
not a special case or a less general discretization of that framework?"

**Audit finding.** This is the closest-work cluster and must be cited and
implemented as a baseline before any theory claim can reopen.

### 4.3 Adaptive histograms and adaptive partitions

Nobel (1996) gives general sufficient conditions for consistency of histogram
regression estimators based on data-dependent partitions. Its motivation is
already spatial allocation: a data-dependent partition can put most cells in
clusters and allocate more cells where responses are erratic. It also proves
consistency for empirically optimal regression trees when tree size grows at an
appropriate rate.

Scott and Nowak (2006) are closer to the classification claim. Their dyadic
decision trees minimize penalized empirical risk exactly and use a spatially
adaptive penalty depending not just on leaf count but also on sample
distribution and tree shape. They derive an oracle inequality and near-minimax
rates, adapting to boundary noise, intrinsic dimension, irrelevant features,
and boundary smoothness.

**Mathematical equivalence.** Both lines select a nonuniform, data-dependent
partition and balance approximation error against partition complexity. The
slogan "put more granules where the task is difficult or valuable" is already
the standard rationale for adaptive partitions.

**Material difference.** A cut of learned cluster balls followed by global
nearest-surface assignment is not an axis-aligned histogram, dyadic partition,
or standard tree classifier. Balls may overlap and their prediction cells need
not match training clusters. No consistency result, oracle inequality, minimax
rate, or valid adaptive penalty currently exists for this representation.

**Potential Reviewer Objection.** "Adaptive partition estimators have allocated
cells nonuniformly for decades, and spatially adaptive tree penalties already
have risk guarantees. What property of overlapping granular balls changes the
rate or the attainable frontier?"

**Audit finding.** High conceptual and theoretical collision. A new cell shape
alone is insufficient; a distinct guarantee or impossibility result is needed.

### 4.4 Rate-distortion and task-aware quantization

Shannon's classical rate-distortion function minimizes information rate over
encoders whose expected distortion is at most `D`. This is not literally the
current optimization:

- `granule_count` is not an expected code length, entropy, or mutual
  information;
- validation classification error is not reconstruction distortion unless a
  task-aware distortion is explicitly defined;
- the experiment has finite, deterministic candidate cuts, not asymptotic block
  codes or stochastic encoders.

Calling the current plot "rate-distortion" without these qualifications would
therefore overclaim equivalence to Shannon theory.

The operational collision is nevertheless severe. Chou et al. already trace
the distortion-rate frontier of pruned tree-structured vector quantizers and
study minimum average length, entropy, and leaf count. Severo, Domanovitz, and
Khisti (2022) further show that quantization can be designed and validation
selected for downstream 0-1 classification rather than reconstruction alone.

**Potential Reviewer Objection.** "Leaf count versus classification loss is an
operational task-aware distortion-resource curve, already covered by
tree-structured quantization. Where are the actual bits or an information-
theoretic bound?"

**Audit finding.** Classical Shannon equivalence is only analogical. Operational
tree-quantizer equivalence is very high. A genuine rate claim must encode the
ball parameters and routing metadata and optimize or bound expected bits.

### 4.5 Coresets and prototype selection

Hart's condensed nearest-neighbor rule established the classical idea of
retaining a smaller labeled subset for nearest-neighbor classification.
Feldman and Langberg (2011) formalize broad coreset constructions as small
weighted representations that approximately preserve an optimization objective
over an entire query family.

The current selected ball stores a center, radius, label/count information, and
weight implicit in its counts; prediction is nearest-surface. It is therefore a
prototype compression method in an application-level sense.

It is **not** presently a coreset in the modern theoretical sense:

- centers need not be input examples;
- there is no `(1 +/- epsilon)` uniform approximation guarantee for all models
  or queries;
- only one fixed granular-ball prediction rule is evaluated;
- test-risk oracle selection does not prove preservation of the full-data
  objective.

**Potential Reviewer Objection.** "This is prototype selection with composite
prototypes. Compare against condensed/reduced NN, k-medoids, clustering
prototypes, and coreset baselines at the same stored bytes."

**Audit finding.** Medium theorem collision but high baseline obligation. The
word `coreset` should not be used for the current method without a uniform
approximation statement.

### 4.6 Structural risk minimization and validation model selection

SRM selects among a hierarchy of hypothesis classes by combining empirical risk
with a complexity term justified by generalization control. Shawe-Taylor et al.
(1998) explicitly handle data-dependent hierarchies. Barron, Birge, and Massart
(1999) develop risk bounds for penalized model selection.

The present candidate cuts form a finite, training-dependent hierarchy (or a
product of ten-element regional hierarchies), and validation chooses a model
under a risk tolerance. This is model selection. It is not yet SRM theory
because it supplies no uniform deviation term, complexity calibration, oracle
inequality, or correction for searching `10^m` configurations.

**Potential Reviewer Objection.** "The selector is holdout model selection over
a finite family. Where is the new complexity measure, risk bound, or selection
guarantee?"

**Audit finding.** High formulation collision. Calling validation tolerance a
new `risk-budget principle` does not create a theoretical contribution.

## 5. Claim-by-claim equivalence map

| Proposed claim | What prior theory already gives | What remains unproved here | Status |
|---|---|---|---|
| A global purity threshold can be worse than regional thresholds | A restricted diagonal policy can be worse than its product policy; exact price-of-uniformity identity above | A granular-ball-specific population lower bound that is not merely class inclusion | **Not novel as stated** |
| Minimize granules under an allowed risk loss | Optimal pruning and TSVQ distortion-cost formulations | Efficient/optimal arbitrary GBC cut under nonadditive nearest-surface routing | **Direct collision** |
| Allocate more granules to valuable/difficult regions | Adaptive histograms, spatial tree penalties, bit allocation | A distinct value estimator with a valid bound under unknown regions | **Direct conceptual collision** |
| Validation-selected nonuniform cut is a method | Holdout model selection/SRM family selection | Generalization after a `10^m` search; scalable optimizer; no test oracle | **Routine model selection** |
| Granule count is a resource rate | Leaf-count complexity and operational codebook size | Actual bytes, latency, expected comparisons, or code length | **Proxy only** |
| Selected balls are a compressed representation | Prototype selection and vector quantization | Coreset-style uniform preservation or task-specific approximation guarantee | **Application-level collision** |
| The current frontier is an oracle upper bound | Oracle model selection/frontier diagnostics are standard | Bias from using the same test set for search and reporting | **Diagnostic only** |

## 6. Potential Reviewer Objections

These are the objections a submission must answer directly, not hide in related
work.

1. **"CART with granular vocabulary."** The objective is error versus number of
   leaves on a fixed maximal tree. Where is the comparison with minimal
   cost-complexity and optimal pruning?
2. **"TSVQ solved this in 1989/1992."** Tree-structured vector quantization
   already treats tree pruning as distortion-rate optimization and includes
   leaf-count budgets and bit allocation.
3. **"The main inequality is tautological."** Since the global family is the
   diagonal subset of the nonuniform product family, its optimum cannot be
   better. A strict synthetic example only shows incompatible local optima.
4. **"Known region identity does the hard work."** The algorithm receives the
   heterogeneous region routing variable. A real method must infer routing or
   use an observed, deployment-valid context without label leakage.
5. **"The oracle searches the test set."** Positive test-oracle regret is
   optimistically biased and cannot be presented as method performance.
6. **"The algorithm does not optimize arbitrary cuts."** It selects one of ten
   purity cuts per region and enumerates `10^m` combinations. It neither uses
   classic polynomial pruning nor solves the harder granular-ball cut problem.
7. **"The resource is cosmetic."** Leaf count is converted to a rough memory
   formula; measured bytes, pointers, metadata, routing, and inference cost are
   absent from the constraint.
8. **"Adaptive partitions already express local value."** Existing theory has
   spatially adaptive penalties and consistency/minimax results. The submission
   currently offers no stronger guarantee.
9. **"Prototype baselines are missing."** Nearest-surface balls must be compared
   at equal bytes with standard prototype selection, quantization, and coreset-
   inspired summaries.
10. **"The class-mean generator uses labels."** A label-seeded tree is not an
    independent unsupervised granulation mechanism, and it can amplify the
    apparent benefit of task-aware refinement.

## 7. Minimum bar for reopening a standalone theory claim

At least one of the following must be completed. Rewording the same finite
frontier is not enough.

### Route A: solve the granular-ball-specific cut problem

Define the candidate class as all valid cuts of one maximal granular-ball tree
or forest, retain nearest-surface prediction, and establish at least one of:

- computational complexity or hardness caused by cross-ball routing
  interactions;
- an exact or approximation algorithm with a stated guarantee;
- a bound relating overlap/radius geometry to the nonadditivity gap;
- a condition under which the objective becomes node-additive and classical
  pruning is recovered as a special case.

Baselines must include CART weakest-link pruning, Bohanec-Bratko-style optimal
size/error pruning, and the Lin et al. leaf-budget dynamic program wherever
their assumptions apply.

### Route B: prove a population result that depends on granular geometry

A valid lower bound must do more than compare a diagonal policy class with its
product relaxation. It should specify unknown-region routing and show how
center/radius estimation, overlap, density, and sample size force an excess-risk
or resource gap that a standard adaptive partition theorem does not already
cover. The bound must survive replacing global purity by an optimal classical
subtree.

### Route C: make the resource operational

Encode centers, radii, counts, labels, tree/routing metadata, and precision.
Optimize actual expected bits, measured bytes, latency, or distance evaluations.
Then compare against tree-structured vector quantization and prototype/coreset
methods on a common rate-risk frontier. A theorem about this encoding may be
distinct; a granule-count plot is not.

### Route D: learn allocation without given regions

Jointly learn a deployment-valid routing function and local refinement under an
honest validation protocol. Provide a complexity correction or oracle inequality
for both routing and cuts. Compare with spatially adaptive DDT/CART-style
penalties. This would address the largest gap between the synthetic existence
result and an algorithm.

## 8. Final novelty decision

```text
Empirical phenomenon:
  RETAINED. Heterogeneous local optima can make one purity threshold Pareto-
  suboptimal on the frozen synthetic families.

Standalone theorem:
  REJECTED IN CURRENT FORM. The price-of-uniformity result is a generic product-
  class identity, not a granular-ball theorem.

Current G3 algorithm:
  REJECTED AS A NOVEL OPTIMIZER. It is exhaustive finite model selection over
  regional pruning-path candidates.

Application/theory explanation:
  P1_APPLICATION_EXPLANATION. It may explain why a strong application benefits
  from nonuniform allocation, provided optimal pruning, adaptive partition,
  TSVQ, and prototype baselines are included.

Collision risk:
  VERY HIGH for objective/formulation;
  HIGH for the adaptive-allocation slogan;
  MEDIUM/UNKNOWN only for a future arbitrary granular-ball cut theorem under
  nearest-surface routing.
```

No paper should claim that resource/risk-constrained nonuniform granularity is
new on the evidence currently in the repository. The only plausible standalone
theory opening is the part classic tree pruning does not model: interacting,
overlapping center-radius representatives with non-hierarchical query routing
and an operational resource constraint.

## 9. Source register

Sources were limited to primary papers/books, author-hosted manuscripts, and
publisher/Crossref-compatible metadata. Bibliographic metadata and DOI targets
were checked on 2026-08-24.

1. Leo Breiman, Jerome H. Friedman, Richard A. Olshen, and Charles J. Stone,
   *Classification and Regression Trees* (original 1984; publisher electronic
   edition 2017), especially the minimal cost-complexity and optimal-pruning
   chapters. [Publisher DOI](https://doi.org/10.1201/9781315139470).
2. Philip A. Chou, Tom Lookabaugh, and Robert M. Gray, "Optimal pruning with
   applications to tree-structured source coding and modeling," *IEEE
   Transactions on Information Theory* 35(2), 299-315, 1989.
   [DOI](https://doi.org/10.1109/18.32124). The public manuscript/metadata states
   the covered applications and the fewest-leaves-at-given-error interpretation.
3. Marko Bohanec and Ivan Bratko, "Trading accuracy for simplicity in decision
   trees," *Machine Learning* 15(3), 223-250, 1994.
   [DOI](https://doi.org/10.1007/BF00993345). Its abstract states the smallest-
   tree-with-specified-accuracy problem and dynamic-programming solution.
4. Jianhua Lin, James A. Storer, and Martin Cohn, "Optimal pruning for tree-
   structured vector quantization," *Information Processing & Management*
   28(6), 723-733, 1992.
   [DOI](https://doi.org/10.1016/0306-4573%2892%2990064-7). The publisher abstract
   gives the leaf-budget `O(nk)` result and hardness of other cost constraints.
5. Andrew Nobel, "Histogram regression estimation using data-dependent
   partitions," *Annals of Statistics* 24(3), 1084-1105, 1996.
   [DOI](https://doi.org/10.1214/aos/1032526958) and
   [author-hosted manuscript](https://nobel.web.unc.edu/wp-content/uploads/sites/13591/2017/01/histreg.pdf).
   The manuscript explicitly motivates allocating cells to clusters and erratic
   response regions and states consistency conditions.
6. Clayton Scott and Robert D. Nowak, "Minimax-optimal classification with
   dyadic decision trees," *IEEE Transactions on Information Theory* 52(4),
   1335-1353, 2006. [DOI](https://doi.org/10.1109/TIT.2006.871056) and
   [author-hosted manuscript](https://www.stat.rice.edu/~cscott/pubs/ddt.pdf).
   The paper gives penalized ERM, spatially adaptive penalties, an oracle
   inequality, and near-minimax adaptation results.
7. Claude E. Shannon, "Coding Theorems for a Discrete Source With a Fidelity
   Criterion," *IRE National Convention Record* 7(4), 142-163, 1959.
   [IEEE record](https://ieeexplore.ieee.org/document/5311476) and
   [public Stanford copy](https://ee.stanford.edu/~gray/itss11.pdf).
8. Daniel Severo, Elad Domanovitz, and Ashish Khisti, "Regularized
   Classification-Aware Quantization," in *30th Biennial Symposium on
   Communications*, 61-73, 2022.
   [DOI](https://doi.org/10.1007/978-3-031-06947-5_5) and
   [public preprint](https://arxiv.org/abs/2107.09716).
9. Peter E. Hart, "The Condensed Nearest Neighbor Rule," *IEEE Transactions on
   Information Theory* 14(3), 515-516, 1968.
   [DOI](https://doi.org/10.1109/TIT.1968.1054155).
10. Dan Feldman and Michael Langberg, "A Unified Framework for Approximating and
    Clustering Data," *STOC 2011*, 569-578.
    [DOI](https://doi.org/10.1145/1993636.1993712) and
    [public full version](https://arxiv.org/abs/1106.1379).
11. John Shawe-Taylor, Peter L. Bartlett, Robert C. Williamson, and Martin
    Anthony, "Structural risk minimization over data-dependent hierarchies,"
    *IEEE Transactions on Information Theory* 44(5), 1926-1940, 1998.
    [DOI](https://doi.org/10.1109/18.705570).
12. Andrew R. Barron, Lucien Birge, and Pascal Massart, "Risk bounds for model
    selection via penalization," *Probability Theory and Related Fields* 113,
    301-413, 1999. [DOI](https://doi.org/10.1007/s004400050210).

## 10. Audit boundary

This is a forced closest-work audit, not a claim of bibliographic exhaustiveness.
It is sufficient for a negative novelty decision because multiple independent
primary sources already cover the proposed objective more generally. A future
positive claim would still require a fresh search focused on arbitrary cuts of
overlapping ball covers, additively weighted Voronoi classifiers, and resource-
constrained prototype forests after the exact new theorem is written.
