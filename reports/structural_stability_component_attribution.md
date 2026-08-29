# Structural Stability Component Attribution v1

This frozen follow-up holds each original/perturbed granular representation fixed and changes only the prediction rule. It contains 320 rows: four pre-frozen scenarios, five complete perturbation seeds, four repository implementations, and four decision rules. No new dataset, severity, generator, or seed was added after the cheap-test outcome.

## Decision-level means

| decision_rule | prediction_agreement | accuracy_original | accuracy_perturbed | decision_accuracy_gain_original_vs_nearest | decision_accuracy_gain_perturbed_vs_nearest |
|---|---|---|---|---|---|
| native_radius_aware | 0.7084 | 0.7203 | 0.6708 | -0.0662 | -0.1251 |
| nearest_center | 0.8983 | 0.7865 | 0.7959 | 0.0000 | 0.0000 |
| radius_aware_distance | 0.7084 | 0.7203 | 0.6708 | -0.0662 | -0.1251 |
| three_center_inverse_distance_vote | 0.8788 | 0.7869 | 0.7858 | 0.0004 | -0.0102 |

`native_radius_aware` is exactly equal to `radius_aware_distance` for these v1 repository implementations: **YES**. This equality is an implementation fact, not evidence that paper-native rules are universally equivalent.

## Generator-ranking sensitivity

Each row below compares the generator ranking by prediction agreement under a decision with the ranking under nearest-center for the same dataset, perturbation and seed. Pairwise reversals exclude tied comparisons.

| decision_rule | kendall_tau_vs_nearest | pairwise_rank_reversal_rate | best_generator_retained |
|---|---|---|---|
| native_radius_aware | 0.2987 | 0.3350 | 0.3500 |
| nearest_center | 1.0000 | 0.0000 | 1.0000 |
| radius_aware_distance | 0.2987 | 0.3350 | 0.3500 |
| three_center_inverse_distance_vote | 0.8759 | 0.0433 | 0.6500 |

The three-center vote has mean Kendall tau 0.8759 against nearest-center and retains the same best generator in 65% of frozen conditions. Radius-aware/native prediction has substantially lower rank agreement and only 35% best-generator retention.

Decision: `STRUCTURAL_STABILITY_COMPONENT_SENSITIVE`. The representation-level decoupling remains present, but the observed predictive-stability ranking is not generator-only: changing the fixed structure's decision rule changes both agreement and rank ordering. This supports the narrow conceptual claim that structural stability, predictive stability, and decision-rule stability must be reported separately. It does not yet support a universal author-method ranking.
