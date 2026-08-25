# 2024--2026 Granular-Ball Application Literature Boundary

## Scope

Search date: 2026-08-25. The search targeted granular-ball work in industrial
fault diagnosis, finance/credit/fraud, IIoT intrusion, medical diagnosis, and
combinations with XGBoost, LightGBM, CatBoost, Random Forest, ExtraTrees,
boosting, and KNN.

Evidence labels are conservative:

- `Published`: DOI and publisher/bibliographic record verified;
- `Preprint/author manuscript`: accessible manuscript but final venue not verified;
- `publisher abstract/sections`: enough to code the high-level mechanism, not
  enough to claim exact datasets, splits, baselines, or gains absent from the page;
- `no direct hit found`: scoped search result, not proof of non-existence.

The machine-readable record is
`literature/application_scout/application_collision_matrix.csv`.

## Required-paper audit

### MgBIF: noisy-label fault diagnosis is directly occupied

*Like draws to like: A Multi-granularity Ball-Intra Fusion approach for fault
diagnosis models to resists misleading by noisy labels* was published in
Advanced Engineering Informatics (2024), DOI
`10.1016/j.aei.2024.102425`.

The method constructs per-sample, multi-granularity neighborhoods in a latent
space, fuses neighbor labels to correct labels, estimates noise intensity using
purity, and selects high-confidence samples. The paper evaluates three bearing
datasets, of which two are open and one is self-made. Its abstract reports over
96% accuracy at low noise and a maximum improvement of 80% under high noise.

Implication: a new paper cannot claim novelty from “GB suppresses noisy labels
in fault diagnosis.” The open opportunity is a simpler conventional-ML route,
leakage-safe signal splits, more independent public sources, and equal-budget
strong baselines.

### WGBRS: weighted GB feature selection for bearing diagnosis is occupied

*Weighted granular-ball rough sets: A granular learning framework for robust
feature selection and fault diagnosis* is a 2026 Pattern Recognition article,
DOI `10.1016/j.patcog.2026.114416`.

It weights granular balls by size/purity inside a rough-set approximation and
uses weighted dependency for feature selection. A rolling-bearing application
with added noise is reported. Exact bearing source, split, classifier, and
numeric gain require full-table access.

Implication: rough-set feature selection plus ball weighting is crowded. This
application scout should not reproduce that stack.

### GDNN: imbalanced deep fault diagnosis is occupied

*A Unified Deep Neural Network Framework With Granular Ball Embedding for
Imbalanced Fault Diagnosis: Design and Analysis* is published in IEEE
Transactions on Industrial Informatics, DOI `10.1109/TII.2025.3643425`.

It forms class-specific GB structures in a learned latent space and adds a
justifiable-granularity loss to an end-to-end DNN. Two industrial processes and
multiple imbalanced settings are reported.

Implication: end-to-end GB embedding for imbalanced industrial diagnosis is
already a high-level direct collision. A conventional tree-model augmentation
must be experimentally simpler and must compare against this paper only where
dataset/split/metric alignment is possible.

### GB-RVFL: biomedical GB model and public code exist

GB-RVFL is published in Pattern Recognition (2025), DOI
`10.1016/j.patcog.2024.111142`. It replaces samples by GB centers in an RVFL
closed-form learner; GE-GB-RVFL adds graph embedding. Experiments include KEEL,
UCI, NDC, BreakHis breast cancer, and ADNI Alzheimer data. Public code exists at
`MdSajid1044/GB-RVFL`.

Implication: medical tabular/image-derived classification is not empty, and a
simple `GB + shallow model` claim would face this direct comparator.

### GAdaBoost: GB-based boosting under label noise is occupied

GAdaBoost is published in Knowledge-Based Systems (2025), DOI
`10.1016/j.knosys.2025.113898`. It granulates data and runs a GB-based SAMME
variant to reduce redundant computation and label-noise sensitivity.

Implication: “GB + boosting” is not empty. However, the scoped search found no
formal priority-domain paper directly combining standard GB structural
features or cross-fitted reliability weights with XGBoost, LightGBM, or
CatBoost.

### PCA-GRF: granular Random Forest for small generic data is occupied

PCA-GRF is published in Information Sciences (2026), DOI
`10.1016/j.ins.2026.123446`. It combines adaptive PCA, cross-dimensional
multi-granularity features, and Random Forest on 25 UCI datasets capped at
1,000 samples. The publisher abstract reports gains above 20% for datasets where
plain RF is weak.

Implication: small-sample granular RF is occupied at a generic benchmark level,
but this is not a verified granular-ball industrial/finance/IIoT application.

### IIoT: one strong direct collision already covers six datasets

*Intrusion Detection in Industrial Internet of Things Based on Granular-Ball
Intuitionistic Fuzzy Sets* is published in IEEE Transactions on Fuzzy Systems
(2026), DOI `10.1109/TFUZZ.2026.3669922`.

The abstract lists X-IIoTID, TON_IoT, WUSTL-IIOT, KDDCUP99, NSL-KDD, and
UNSW-NB15. It uses class-wise GB generation, intuitionistic-fuzzy patterns, and
an improved fuzzy distance.

Implication: IIoT is no longer a low-collision application. Any retained route
must use leakage-safe time/scenario/device splits, strong boosted-tree baselines,
and a materially simpler mechanism or a gain above the higher predeclared bar.

### Medical: robust GB twin-SVM is directly occupied

*Granular-ball rough set for robust twin support vector classification in
medical image detection* is published in Applied Soft Computing (2026), DOI
`10.1016/j.asoc.2026.115875`. It evaluates synthetic, benchmark, and real
medical-image datasets, with emphasis on noise robustness.

Implication: the medical backup is crowded around SVM/twin-SVM, rough sets, and
GB-RVFL. It is not the cleanest route for a simple conventional tree paper.

## Conventional-model combination search

### XGBoost

No 2024--2026 formal direct hit was found for standard granular-ball structural
features or reliability weights combined with XGBoost in the four priority
domains.

### LightGBM

No formal direct `granular-ball + LightGBM` hit was found in the scoped search.

### CatBoost

No direct priority-domain hit was found. A 2026 haze-risk article combines
multi-granularity GB feature engineering, entropy PCA, swarm-optimized CatBoost,
and risk-system components. It is evidence that the literal combination is not
globally novel, but its multi-module environmental route is explicitly outside
this project's design discipline.

### Random Forest / ExtraTrees

PCA-GRF occupies generic small-sample granular Random Forest. A 2025 conference
book contains a “Granular Ball Random Forest for Robust Classification” abstract,
but no formal full paper was verified. No direct `GB + ExtraTrees` paper was
found.

### KNN and SVM

These combinations are crowded from the original GBC framework onward. They
remain baselines only.

## Domain findings

### Industrial fault diagnosis

Direct positive evidence exists for:

- noisy labels (MgBIF and related MgCNL manuscript);
- imbalanced deep fault diagnosis (GDNN);
- weighted GB rough-set feature selection for noisy bearing diagnosis (WGBRS).

The domain is attractive because difficult settings are real and measurable:
few-shot, class imbalance, label noise, sensor noise, and cross-condition or
cross-machine transfer. It is also becoming crowded, especially for deep GB
embedding and noisy labels.

### Finance and fraud

The scoped search found no direct formal GB credit-scoring, loan-default, or
financial-fraud application paper. Several generic GB anomaly papers mention
fraud as motivation, but that is not domain evidence.

This creates the largest literature space for conventional boosted trees, but
the current GB-positive evidence is weak. The route is worth a cheap test, not a
novelty claim.

### IIoT and intrusion

GBIFS directly occupies the problem with six named datasets. Power-IoT FBOD is
another nearby 2026 application. The domain still has high application value and
many public datasets, but random flow splits are frequently leaky and the
novelty/performance bar is now high.

### Medical diagnosis

GB-RVFL and GB-RGTSVM provide direct medical collisions. Dataset access,
patient-level splitting, and image feature extraction make reproduction harder.
Medical remains a backup only.

## Literature decision

1. Keep industrial fault diagnosis as the first experimental line because it
   has the strongest direct evidence that GB local structure helps under real
   difficult conditions, while a simple conventional-ML feature/weight route is
   not yet directly occupied.
2. Keep finance as the second line because the literature space and tree-model
   fit are strongest, despite weak direct GB evidence.
3. Treat IIoT as a high-bar screen because GBIFS already covers the obvious
   application claim.
4. Defer medical unless the first three lines fail.

