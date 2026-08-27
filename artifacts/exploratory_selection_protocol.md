# Exploratory Selection Protocol: Effect-Rich, Not Cherry-Picked

The aim is not a universal granular-ball privacy claim. The exploratory screen
may deliberately include conditions where refinement could plausibly matter:
moderate-to-high dimensional numeric data, limited per-class support, class
overlap, and a nontrivial refinement trajectory. These are pre-result inclusion
properties, not criteria derived from attack AUC.

## Dataset tiers

- **Effect-opportunity tier:** Breast Cancer, Wine, Digits, Ionosphere, Sonar,
  and Banknote. They jointly span low/high dimension, small/moderate sample
  counts, binary/multiclass labels, and differing overlap.
- **Challenge/negative tier:** later additions must include at least one larger
  or simpler numeric task. This prevents a result on fragile small data from
  being presented as broadly representative.

Every retrievable dataset in a frozen tier is retained. A download or numerical
failure is recorded as such; it is not silently replaced after outcomes appear.

## Regime-first discovery and confirmation

The initial real-data screen is not a universal claim gate. If its aggregate is
weak, the next step is a synthetic regime search over separation, density ratio,
minority fraction, local modes, noise, redundant features, and dimensionality.
All parameter points are stored. The aim is to identify a structural condition
that changes refinement, then release leakage, and finally the GB-versus-KMeans
contrast.

Any apparent regime is only a discovery result. Its condition is then frozen
and must be evaluated on new synthetic seeds, held-out nearby parameter points,
and targeted real datasets selected from metadata rather than attack outcomes.
The project may continue on a stable conditional effect even when no broad
average effect exists. It is killed only when no reproducible regime survives
matched controls and confirmation.

## Seed rule

The initial seeds are fixed at `1, 7, 21, 42, 2026`. Exploratory reporting uses
their full distribution. A promising dataset/threshold may enter confirmation
with a predeclared extension to ten seeds, but the confirmation seed set is not
selected by prior attack performance. No single best seed is reported as a
method result.

## Interpretation

“Good” means an interpretable, reproducible mechanism contrast surviving the
matched-k KMeans control—not merely high leakage. Results may support a scoped
condition such as small-ball release risk. They may not be relabeled a general
granular-ball privacy advantage or disadvantage without heterogeneous
confirmation evidence.
