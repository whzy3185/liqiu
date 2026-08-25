# Privacy/security novelty boundary (2022-2026)

## Scope and search discipline

This is a scoped novelty reconnaissance, not proof of non-existence. Searches
were run on 2026-08-25 over publisher/DOI pages, arXiv, Crossref-indexed records,
and targeted web queries. Preprints are marked separately. Negative statements
below mean "no direct work was found in this scoped search".

Queries included all combinations requested in the research brief, with special
follow-ups for membership inference, reconstruction attack, differential
privacy, public auditing, multiparty auditing, secure aggregation, homomorphic
encryption, image encryption, fuzzy rough feature selection, and cryptographic
compression.

## Answers to the five boundary questions

### Q1: What has "granular-ball privacy" actually shown?

The direct hit is GrBFL (PS001), currently an arXiv preprint. It changes image
inputs into coarse granular-rectangle graphs and reports harder gradient-based
image reconstruction; its supplement is said to include membership inference.
This is empirical attack resistance caused by information loss. It is not a
differential-privacy guarantee, information-theoretic privacy, or cryptographic
confidentiality. FedOC-GB (PS002) avoids centralizing raw intent data but uploads
models and granular-ball knowledge; non-transmission of raw records is not by
itself a leakage bound.

### Q2: Is there a systematic summary-to-attack study?

No direct study was found that treats tabular `center/radius/count/purity` as the
released object and jointly measures membership inference, sensitive-attribute
inference, and prototype reconstruction against matched KMeans/random/
hierarchical partitions. GrBFL is the closest collision, but its object,
attacker, and data modality differ.

### Q3: Is there formal granular-ball plus differential privacy work?

No direct published or accepted hit was found. Two close collisions matter:
3WADD (PS006) applies three-way attribute triage before DP, and F3WDS (PS005)
combines federated three-way decisions with stated DP bounds. Neither uses
granular balls. Any first experiment here must be labelled an empirical noise
prototype until sensitivity and composition are proved.

### Q4: Is there granular-ball cloud/public/multiparty auditing work?

No direct hit was found for cloud-storage integrity, PDP/PoR sampling, public
auditing, or malicious multi-auditor aggregation. F3WDS is multicloud resource
scheduling, not storage-integrity auditing. This lowers collision risk but does
not establish that GB is needed; risk scoring, trees, KMeans, and local methods
are the stronger competing explanations.

### Q5: Is granularity used as cryptographic compression?

There is adjacent work on hierarchical aggregation, encrypted multi-resolution
data, prototype/cluster transmission, and cryptographic batching, but no direct
hit using granular-ball summaries as the pre-HE/MPC compression object. The
idea remains high risk because ordinary microclusters or KMeans prototypes may
provide the entire benefit.

## Density and recommendation matrix

| Direction | Existing-work density | Novelty risk | Cheap-test cost | Recommendation |
|---|---:|---:|---:|---|
| GB tabular summary leakage | 1/5 | 2/5 | 1/5 | Highest priority: direct falsifiable gap |
| Differentially private GB | 1/5 direct, 3/5 adjacent | 3/5 | 2/5 | Gate on leakage result and formal sensitivity |
| GB cloud risk-adaptive auditing | 0/5 direct, 2/5 adjacent | 2/5 | 1/5 | Highest priority, but GB-specificity is doubtful |
| GB multi-auditor trust | 0/5 direct | 2/5 | 1/5 | Run only after stronger two directions |
| GB before HE/MPC/secure aggregation | 0/5 direct, 4/5 generic | 4/5 | 2/5 | High baseline-collision risk |
| Selective image privacy | 2/5 | 4/5 | 3/5 | Defer; GrBFL and image-granulation overlap |
| Fuzzy/rough privacy feature selection | 2/5 direct/adjacent | 4/5 | 3/5 | Formal MPC/FHE feature selection sets a high bar |

## Strongest competing explanation

Every apparent privacy or efficiency gain may be caused by lossy aggregation,
matched prototype count, label-aware partitioning, or ordinary risk
stratification. Therefore the first experiments fix representative count and
budget, and treat KMeans, hierarchical clustering, random groups, and tree
leaves as first-class controls.

