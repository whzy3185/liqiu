# Research map

## Scope and evidence boundary

This first-pass map covers **160** deduplicated papers: **73** abstract-coded and **87** metadata-only.
Counts reflect controlled title/abstract tags, not completed full-text reviews. In
particular, missing split/merge/stop criteria must not be interpreted as absence of those
mechanisms in the paper.

## Task

| Component | Papers |
|---|---:|
| decision analysis | 92 |
| classification | 35 |
| feature selection | 29 |
| clustering | 18 |
| anomaly/outlier detection | 12 |
| stream/online learning | 7 |
| graph learning | 3 |
| regression | 1 |
| recommendation | 1 |

## Representation

| Component | Papers |
|---|---:|
| granular ball | 75 |
| rough-set approximation | 75 |
| points/objects or not reported | 43 |
| fuzzy granule | 22 |
| rough-set neighborhood | 19 |
| shadowed set | 6 |
| graph | 4 |
| interval granule | 1 |

## Granulation

| Component | Papers |
|---|---:|
| granular-ball generation | 75 |
| fuzzy | 22 |
| neighborhood | 19 |
| multi-granulation | 6 |
| adaptive/dynamic | 5 |
| local-density | 4 |
| hierarchical/multi-level | 3 |

## Uncertainty

| Component | Papers |
|---|---:|
| three-way boundary/defer region | 97 |
| fuzzy membership | 17 |
| probabilistic | 11 |
| entropy | 10 |
| purity proxy | 3 |

## Decision

| Component | Papers |
|---|---:|
| three-way accept/defer/reject | 88 |
| classification decision | 35 |
| ranking/selection | 29 |
| cluster assignment | 18 |

## Downstream

| Component | Papers |
|---|---:|
| rough-set reducer | 29 |
| SVM | 4 |
| neural network | 3 |
| kNN | 3 |
| graph neural network | 2 |

## Noise

| Component | Papers |
|---|---:|
| outliers | 8 |
| label noise | 2 |

## Repeated component signatures

| Signature | Papers |
|---|---:|
| points/objects or not reported → unresolved → three-way accept/defer/reject → unresolved | 34 |
| rough-set approximation → unresolved → three-way accept/defer/reject → unresolved | 15 |
| granular ball → granular-ball generation → cluster assignment → unresolved | 7 |
| rough-set approximation + fuzzy granule → fuzzy → three-way accept/defer/reject → unresolved | 6 |
| granular ball → granular-ball generation → unresolved → unresolved | 6 |
| granular ball + rough-set approximation → granular-ball generation → ranking/selection → rough-set reducer | 5 |
| granular ball + rough-set neighborhood + rough-set approximation → granular-ball generation + neighborhood → classification decision + ranking/selection → rough-set reducer | 4 |
| granular ball + rough-set approximation + fuzzy granule → granular-ball generation + fuzzy → ranking/selection → rough-set reducer | 4 |
| granular ball + rough-set approximation + fuzzy granule → granular-ball generation + fuzzy → unresolved → unresolved | 4 |
| granular ball + rough-set neighborhood + rough-set approximation → granular-ball generation + neighborhood → ranking/selection → rough-set reducer | 3 |
| shadowed set → unresolved → three-way accept/defer/reject → unresolved | 3 |
| granular ball + rough-set approximation → granular-ball generation → unresolved → unresolved | 3 |
| rough-set neighborhood + rough-set approximation → neighborhood → unresolved → unresolved | 3 |
| points/objects or not reported → unresolved → three-way accept/defer/reject + classification decision → unresolved | 3 |
| granular ball → granular-ball generation → three-way accept/defer/reject → unresolved | 2 |

## What can already be said

1. Granular-ball rough/neighborhood-rough representations, feature selection, and
   three-way decisions recur often enough to warrant a dedicated collision cluster.
2. Many records cannot yet be distinguished at split/merge/stop level. A claim that
   papers merely swap one component would therefore be premature.
3. Agent, RAG, conformal calibration, and OOD intersections did not enter the retained
   top corpus in material numbers under the high-precision title filter. This is a search
   gap, not evidence of novelty; each needs a separate problem-oriented collision search.
4. The sharp 2024–2026 rise in retained records makes 2026 source verification especially
   important before novelty judgments.

## Required full-text audit

Upgrade representative papers in each high-frequency signature and explicitly extract
split, merge, stop, uncertainty, datasets, baselines, gains, author limitations, and code.
Only after that audit should repeated introductions be used to infer a common structural
defect or to answer why generation algorithms keep being proposed.
