# Granular-Ball-only literature gap scan — 2026-08-25

## Scope rule

Every candidate must concern granular-ball representation, generation, split,
merge, stop, decision distance, uncertainty or update. Application names do not
count as novelty.

## Noisy labels / data quality

- Direct occupied work: Granular Ball Sampling for Noisy Label or Imbalanced
  Classification (10.1109/TNNLS.2021.3105984); G-GBC Gaussian-mixture granular
  balls for noisy CNN classification (10.1016/J.KNOSYS.2026.115754); granular-ball
  representation learning for CNN label noise (2025 LNCS).
- Collision risk: HIGH for another robust classifier/sampler.
- Remaining mechanism question: when a purity target causes the generator to
  chase random/boundary label noise, how does clean-test risk trade against ball
  explosion? A reusable failure map may remain valuable.

## Imbalance / minority structure

- Direct occupied work: GBSampling; three-way hybrid granular-ball sampling;
  GBRIP; granular classifiers for imbalanced data; informed granular-ball
  oversampling.
- Collision risk: HIGH.
- Remaining mechanism question: majority labels and purity stops may erase
  locally dense/disconnected minority regions. Continue only if a cross-family
  minority-recall failure is not repaired by existing sampling baselines.

## Shift / TTA / OOD / uncertainty

- Exact Granular-Ball Test-Time Adaptation titles were not found.
- Adjacent occupied work: open continual feature selection via GB knowledge
  transfer, three-way incremental shadowed GBC, federated open intent GB
  representation, fuzzy GB uncertainty-invariance, entropy uncertainty feature
  selection and generic TTA/OOD/selective prediction.
- Collision risk: MEDIUM for a GB-specific update mechanism; HIGH for “GB + TTA”.
- Remaining mechanism question: purity is fitted on old labels and radius is
  fitted on old geometry. Under shift, do they fail as confidence/coverage
  signals before point prediction fails?

## Dynamic split / merge / shape

- Local dynamic granular-ball outlier detection and manifold GB clustering exist.
- Ellipsoid/manifold replacement is not treated as open by default.
- Collision risk: MEDIUM–HIGH.
- Reopen only after a stress test identifies a shape/update failure that a
  spherical static ball cannot express.

## Active learning / conformal

- Exact GB active-learning and GB conformal titles are sparse, but both are
  generic task-migration traps. Earlier conformal audit showed generic RF
  conformal is more efficient than purity probabilities.
- Decision: no implementation without a new GB-specific property.

## Cheap-test queue

1. Purity-chasing label-noise fragmentation — highest priority failure audit.
2. Minority masking under sample/density heterogeneity — high collision, strict
   kill threshold.
3. Shift-induced purity/radius confidence failure — novelty possible only after
   stable cross-shift evidence.

No candidate is P0 before these tests.
