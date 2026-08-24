# GBGC paper and public-artifact audit

Audit date: 2026-08-24 (Asia/Shanghai)

## Decision

`HOLD_NOT_EXECUTABLE`: GBGC is a mandatory conceptual comparator for the GNN
granularity line, but the named public GitHub repository is not an author-code
release. At the audited commit it contains only a three-page appendix PDF. It
has no source code, license, data, environment manifest, executable entry point,
or test. Consequently, no author-code CPU smoke test can be run and GBGC must
not be represented as a reproduced baseline.

The paper is directly adjacent to the proposed question of assigning different
granularities to different graph regions. It does not, however, formulate a
finite global resource budget, estimate marginal downstream value, or expose a
risk-resource frontier. Use it as closest prior work and as a clean-room
specification candidate only after the ambiguities below are resolved.

## Audited sources and identity

- Paper: [arXiv:2506.19224v1](https://arxiv.org/abs/2506.19224), submitted
  2025-06-24; IJCAI 2025 paper, "GBGC: Efficient and Adaptive Graph Coarsening
  via Granular-ball Computing."
- Named supplementary repository:
  [Wangwangguanguan/Supplementary-materials](https://github.com/Wangwangguanguan/Supplementary-materials),
  pinned to commit
  [`306c60bbf88293937a5e56931055a4854c4fc625`](https://github.com/Wangwangguanguan/Supplementary-materials/tree/306c60bbf88293937a5e56931055a4854c4fc625)
  from 2025-05-14.
- Repository tree at that commit: one 151,876-byte file,
  [`GBGC_Appendix.pdf`](https://github.com/Wangwangguanguan/Supplementary-materials/blob/306c60bbf88293937a5e56931055a4854c4fc625/GBGC_Appendix.pdf)
  (Git blob `6556c9f1860d9f2a5839fde21128750555ed65c7`, SHA-256
  `9e1710eabeacc3df3f398eddf297fb8d160ffd9b7c7919dc3bdd6aab5a353769`).
  Git history has one commit, one branch (`main`), no tags, and the PDF has zero
  embedded files.
- The paper separately says that code is available at
  `https://anonymous.4open.science/r/GBGC`. On the audit date, that URL
  redirected to `/api/repo/GBGC/file/` and returned HTTP 401 with
  `{"error":"not_connected"}`. It therefore cannot supply the missing code.

The paper, arXiv source, appendix PDF, Git tree, GitHub API tree, and anonymous
endpoint were checked independently. Search results did not reveal another
author implementation. This is an availability statement for the audit date,
not proof that code never existed.

## License

| Artifact | Finding | Reuse consequence |
|---|---|---|
| GitHub repository / alleged code | No `LICENSE`, package metadata, or license declaration; GitHub API reports `license: null`. | Do not copy or redistribute implementation material. There is no implementation to execute in the audited tree in any case. |
| Appendix PDF | No software license in the repository or PDF. | Treat as a paper supplement, not licensed source code. |
| arXiv paper/source | arXiv's non-exclusive distribution license. | This permits arXiv to distribute the article; it is not an open-source software license for an implementation. |

Any future clean-room implementation must be original, cite the paper, and
record its own license. It must not be labeled author code.

## Paper method and key parameters

The paper specifies a topology-only, coarse-to-fine procedure:

1. Split disconnected input into connected components.
2. For each component, initialize granular-balls using highest-degree centers
   and BFS, with a nominal scale of `sqrt(N)`.
3. Define ball quality as `internal_edges / nodes + transitivity`.
4. Select the two highest-degree nodes in a ball, grow two BFS regions, and
   assign each other node to the center that reaches it first.
5. Accept a split when the sum of the two child qualities is greater than the
   parent quality; recurse otherwise retaining the parent.
6. Make each final ball a supernode and add a superedge when any original edge
   crosses the corresponding balls.

The adaptive algorithm has no externally selected coarsening ratio. The paper's
non-adaptive Algorithm 4 accepts `r in (0, 1)` and sensitivity analysis sweeps
`r` in increments of 0.1, but the score used to choose the next ball is only
described verbally. The paper reports complexity
`O(N^(3/2) + E sqrt(N))`.

The reported experimental environment is Python 3.10.9, PyTorch 1.13, CUDA
11.6, and NetworkX 2.8 on an Intel Xeon Gold 5218 CPU and four Tesla V100 GPUs.
The classifier is 1-nearest-neighbor. The paper mentions multiple random seeds,
cross-validation, and repeated runs, but gives neither seed values, fold count,
split files, nor complete classifier/preprocessing settings.

## Datasets and reported adaptive ratios

The paper evaluates graph classification collections, not a single-graph node
classification task. No dataset files, download script, split indices, checksums,
or dataset-license records are included in the public repository.

| Dataset | Graphs | Mean nodes | Mean edges | Reported adaptive ratio `r_a` |
|---|---:|---:|---:|---:|
| MUTAG | 188 | 17.93 | 19.79 | 0.35 |
| PROTEINS | 1,113 | 39.06 | 72.82 | 0.24 |
| IMDB-BINARY | 1,000 | 19.77 | 96.53 | 0.19 |
| NCI109 | 4,127 | 29.68 | 32.13 | 0.38 |
| DHFR | 756 | 42.43 | 44.54 | 0.35 |
| BZR | 405 | 35.75 | 38.36 | 0.40 |
| Tox21_AR-LBD-testing | 253 | 21.85 | 22.73 | 0.34 |
| OVCAR-8H | 39,253 | 46.67 | 48.70 | 0.38 |
| P388H | 40,651 | 40.45 | 41.89 | 0.37 |
| SF-295H | 39,030 | 46.65 | 48.68 | 0.38 |
| DD | 1,178 | 284.32 | 715.66 | 0.20 |

The large `Size` values for OVCAR-8H, P388H, and SF-295H are counts of many
small graphs; they do not establish behavior on one citation graph with
thousands of nodes.

## Output interface audit

The article defines a binary membership matrix `C` of shape
`N x N_coarse` and writes `L_coarse = C^T L C`. In prose, the output is a
coarsened graph whose supernodes are granular-balls. The appendix is less
consistent:

- Algorithm 1 declares `Original Graph -> Coarsening Graph`.
- Algorithm 2's heading declares a list of granular-ball graphs, but its last
  steps construct and return a coarsened graph.
- Algorithms 3 and 4 declare a list of granular-balls.

There is no callable API and no documented object schema or serialization
format. In particular, the public artifact supplies none of the objects needed
for a Planetoid/GNN adapter: membership vector or `C`, coarse edge weights,
coarse node features, coarse labels, train/validation/test masks, or a lifting
map for node-level predictions. The paper defines only topology-level
aggregation and a binary existence rule for superedges.

## Paper/artifact deviations and unresolved choices

There is no source code to compare line-by-line with the paper. The following
paper-to-public-artifact gaps and specification conflicts are therefore material:

| ID | Paper or appendix statement | Public artifact / conflict | Consequence |
|---|---|---|---|
| D1 | Footnote says code is available from Anonymous GitHub. | Anonymous endpoint is disconnected; named GitHub repository contains only the appendix. | Author-code reproduction is blocked. |
| D2 | Introduction says initialization calculates distances between all node pairs. | Method and pseudocode initialize with highest-degree centers and BFS; no all-pairs distance appears. | Initialization semantics and complexity claim do not align. |
| D3 | Main text says BFS continues until the number of nodes at a layer exceeds `sqrt(N)` and describes `sqrt(N)` initial balls. | Algorithm 2 stops before `current_ball + layer_nodes` exceeds `sqrt(N)`, which caps ball size and does not guarantee exactly `sqrt(N)` balls. | A clean-room partition can differ immediately. |
| D4 | GBGC is described as randomness-free. | Degree ties, simultaneous-BFS ties, adjacency iteration order, and disconnected/tiny-ball cases have no deterministic tie rules. | Exact partitions are under-specified even without a random generator. |
| D5 | `internal_edges / nodes` is called average degree; transitivity is added. | For an undirected graph average degree is `2E/N`, and no convention is given when a ball has zero connected triples. | Split decisions depend on an unstated factor and zero-denominator rule. |
| D6 | Superadjacency is binary if any crossing edge exists. | `C^T L C` preserves crossing-edge multiplicity as weights. | The graph used for classification and the graph used in the spectral argument may differ. |
| D7 | Theorem 1 assumes binary `C` is approximately orthogonal and uses both `C^T C approx I` and `C C^T approx I`. | For a membership matrix, `C^T C` is the diagonal of ball sizes and `C C^T` has within-ball blocks, unless `C` is normalized and the projection is redefined. | The stated spectral guarantee cannot be used as an implementation oracle. |
| D8 | Non-adaptive Algorithm 4 chooses a ball by size and quality difference. | No formula, normalization, ordering, or tie break is given. | A faithful fixed-budget ratio sweep cannot be reconstructed uniquely. |
| D9 | Paper reports repeated cross-validation and multiple seeds. | No scripts, splits, seeds, logs, or raw results are released. | Classification numbers and uncertainty cannot be independently regenerated. |

These are deviations to disclose, not implementation choices that an adapter may
silently resolve.

## CPU small-graph run

| Check | Result |
|---|---|
| Clone pinned repository | Pass |
| Discover Python/package files | Fail: none present |
| Discover dependency manifest | Fail: none present |
| Discover executable or importable entry point | Fail: none present |
| Discover bundled toy or real data | Fail: none present |
| Inspect PDF for embedded code/files | Pass: zero embedded files |
| Install author environment | Not possible from released artifact |
| Run author GBGC on a CPU toy graph | **Not run / structurally blocked** |

At the algorithm level, highest-degree selection, BFS, and NetworkX transitivity
can all be implemented on CPU, and CUDA is not intrinsically required by the
published pseudocode. That is only a feasibility inference. It is not evidence
that the absent author implementation installs or runs on CPU, nor that its
output matches the paper.

## Cora/Citeseer/PubMed frontier suitability

| Requirement | Cora | Citeseer | PubMed | Finding |
|---|---|---|---|---|
| Author-code executable baseline | No | No | No | No code exists in the audited release. |
| Evidence on a single citation graph | No | No | No | Paper evaluates graph classification collections. |
| Node features/labels/masks preserved | Unspecified | Unspecified | Unspecified | Required output contract is absent. |
| Multiple fixed resource budgets | Unspecified | Unspecified | Unspecified | Adaptive GBGC returns one ratio; fixed-`r` pseudocode is incomplete. |
| CPU runtime/memory evidence | None | None | None | Reported hardware includes four V100s; no CPU-only command or log is available. |
| Eligible for the current confirmation frontier | **HOLD** | **HOLD** | **HOLD** | Not eligible as an author-code result. |

GBGC is therefore **not currently suitable as an executable frontier baseline**
for Cora, Citeseer, or PubMed. It is suitable as:

- a mandatory closest-work citation for adaptive region-dependent graph
  granularity;
- a conceptual comparator whose adaptive ratio supplies one non-budgeted point;
- a future clean-room baseline, explicitly labeled as such, after all D2-D8
  choices are frozen before seeing confirmation results.

Before promotion to the frontier, an implementation must expose at least
`membership/C`, weighted coarse adjacency, aggregated features and labels, mask
handling, and prediction lifting; support a prespecified common node-budget
grid; record wall time and peak memory on CPU; and pass deterministic toy tests
covering disconnected graphs, paths, stars, cliques, isolated nodes, degree
ties, and zero-transitivity balls. Its node-classification evaluation must use
the same data splits and downstream model as every comparator.

## Research implication

GBGC creates a **high conceptual-collision risk** for any claim stated merely as
"allocate finer granularity to complex graph regions." The remaining defensible
gap is narrower: optimize region-wise refinement under an explicit shared
resource budget using a prespecified estimate of marginal downstream risk, then
compare complete risk-node/time/memory frontiers. GBGC neither supplies that
budgeted objective nor an executable release with which to test it, so the next
step should be a disclosed clean-room baseline plus strong licensed graph
coarsening baselines, not an author-code reproduction claim.
