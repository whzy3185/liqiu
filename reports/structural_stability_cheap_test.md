# Structural Stability Cheap Test v1

The frozen v1 test completed all 1280 rows across 8 datasets and 4 explicitly-labelled repository implementations.  The synthetic A3 family is included only as a controlled geometry-label stress family, never as privacy evidence.  The primary decision is common nearest-center prediction on a fixed test split; native decision rules were not used.

The seed-baseline identity rows are controls and are excluded from summary means. Across the remaining 1248 comparisons, mean ARI is 0.6960, mean NMI 0.8199, mean VI 0.8450, mean prediction agreement 0.9002, and mean absolute accuracy change 0.0291.

## Generator means

| generator | ari | nmi | vi | prediction_agreement | accuracy_change | ball_count_ratio |
|---|---|---|---|---|---|---|
| gbc_confidence_bound_control | 0.5826 | 0.8033 | 1.0360 | 0.9068 | 0.0319 | 10.3133 |
| gbc_multiclass_cleanroom | 0.7213 | 0.8438 | 0.7876 | 0.9141 | 0.0256 | 10.2697 |
| tree_class_means_binary | 0.7576 | 0.8226 | 0.7161 | 0.8999 | 0.0284 | 3.6397 |
| tree_kmeans_binary | 0.7226 | 0.8097 | 0.8403 | 0.8802 | 0.0306 | 6.2418 |

## Perturbation means

| perturbation_type | ari | nmi | vi | prediction_agreement | accuracy_change | ball_count_ratio |
|---|---|---|---|---|---|---|
| feature_gaussian | 0.8128 | 0.9141 | 0.5544 | 0.9210 | 0.0117 | 1.0427 |
| label_flip | 0.6539 | 0.7686 | 0.7883 | 0.9091 | 0.0249 | 8.2881 |
| sample_deletion | 0.6186 | 0.7773 | 1.3013 | 0.8535 | 0.0598 | 15.7898 |
| seed | 0.7559 | 0.8830 | 0.6434 | 0.9320 | 0.0115 | 1.0957 |

## Structural--predictive decoupling

Using the pre-frozen descriptive criterion prediction agreement >= 0.95 and ARI <= 0.70, there are 27 cases overall and 19 cases under actual sample, label, or feature perturbations.  The latter span 6 datasets and 3 generators.  They are retained in full below; no threshold, seed, or source was removed.

| dataset | generator | perturbation_type | perturbation_strength | seed | ari | nmi | vi | prediction_agreement | accuracy_change | ball_count_original | ball_count_perturbed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| internet_ads | tree_kmeans_binary | label_flip | 0.05 | 2026 | 0.0000 | 0.0000 | 0.2251 | 0.9780 | 0.0220 | 1 | 5 |
| internet_ads | tree_kmeans_binary | label_flip | 0.05 | 42 | 0.0000 | 0.0000 | 0.2251 | 0.9760 | 0.0200 | 1 | 5 |
| internet_ads | gbc_multiclass_cleanroom | label_flip | 0.05 | 2026 | 0.0000 | 0.0000 | 0.7664 | 0.9680 | 0.0320 | 1 | 20 |
| internet_ads | gbc_multiclass_cleanroom | label_flip | 0.05 | 1 | 0.0000 | 0.0000 | 0.7864 | 0.9640 | 0.0320 | 1 | 26 |
| internet_ads | gbc_multiclass_cleanroom | label_flip | 0.05 | 42 | 0.0000 | 0.0000 | 0.7764 | 0.9620 | 0.0260 | 1 | 23 |
| internet_ads | tree_kmeans_binary | label_flip | 0.05 | 7 | 0.0000 | 0.0000 | 0.9759 | 0.9580 | 0.0380 | 1 | 26 |
| internet_ads | tree_kmeans_binary | label_flip | 0.05 | 21 | 0.0000 | 0.0000 | 0.9657 | 0.9560 | 0.0360 | 1 | 26 |
| htru2 | tree_kmeans_binary | label_flip | 0.1 | 21 | 0.0000 | 0.0000 | 0.8209 | 0.9520 | 0.0280 | 1 | 28 |
| internet_ads | gbc_multiclass_cleanroom | label_flip | 0.05 | 7 | 0.0000 | 0.0000 | 1.7271 | 0.9500 | 0.0460 | 1 | 48 |
| internet_ads | gbc_confidence_bound_control | sample_deletion | 0.01 | 42 | 0.1670 | 0.3833 | 1.5665 | 0.9740 | 0.0060 | 23 | 45 |
| internet_ads | gbc_confidence_bound_control | sample_deletion | 0.01 | 2026 | 0.1705 | 0.3578 | 1.9252 | 0.9760 | 0.0040 | 23 | 69 |
| internet_ads | gbc_confidence_bound_control | sample_deletion | 0.05 | 21 | 0.1725 | 0.2895 | 1.2205 | 0.9940 | 0.0020 | 23 | 25 |
| internet_ads | gbc_confidence_bound_control | sample_deletion | 0.01 | 1 | 0.1733 | 0.3605 | 1.5712 | 0.9700 | 0.0060 | 23 | 43 |
| micromass_pure_species | gbc_multiclass_cleanroom | sample_deletion | 0.01 | 21 | 0.4418 | 0.9595 | 0.4511 | 0.9580 | 0.0070 | 313 | 324 |
| micromass_pure_species | gbc_confidence_bound_control | sample_deletion | 0.01 | 21 | 0.4745 | 0.9643 | 0.4010 | 0.9650 | 0.0000 | 323 | 325 |
| wine | tree_kmeans_binary | sample_deletion | 0.05 | 21 | 0.6420 | 0.7041 | 0.8079 | 0.9778 | 0.0222 | 8 | 3 |
| digits | gbc_confidence_bound_control | sample_deletion | 0.01 | 2026 | 0.6659 | 0.8603 | 1.1231 | 0.9511 | 0.0133 | 118 | 128 |
| dry_bean | gbc_confidence_bound_control | label_flip | 0.01 | 42 | 0.6754 | 0.9107 | 0.7555 | 0.9560 | 0.0040 | 139 | 156 |
| dry_bean | gbc_confidence_bound_control | label_flip | 0.01 | 21 | 0.6956 | 0.9339 | 0.5548 | 0.9620 | 0.0120 | 139 | 142 |

The strongest observed case is `internet_ads` / `tree_kmeans_binary` under `label_flip` strength 0.05 seed 2026: ARI 0.0000, prediction agreement 0.9780, and ball count 1 -> 5.  It is a discovery observation, not a standalone conclusion.

## Ranking comparison and gate

The mean-ARI ranking is `tree_class_means_binary > tree_kmeans_binary > gbc_multiclass_cleanroom > gbc_confidence_bound_control`.  The mean prediction-agreement ranking is `gbc_multiclass_cleanroom > gbc_confidence_bound_control > tree_class_means_binary > tree_kmeans_binary`.  Rankings agree: **NO**.

Decision: `STRUCTURAL_STABILITY_PAPER_TRACK`.  The result clears the empirical cheap-test signal because minor data perturbations yield repeated high-prediction/low-ARI observations across multiple datasets and generators.  However, it establishes neither a universal claim nor author-method ranking: all v1 implementations are labelled clean-room/internal controls.  The permitted next step is a frozen, targeted component-attribution confirmation; do not expand datasets, perturbation levels, or author-method claims first.
