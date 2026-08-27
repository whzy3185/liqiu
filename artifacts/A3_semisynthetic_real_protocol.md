# A3 Semi-Synthetic Real-Feature Intervention

Natural Sonar and Spambase did not meet the full frozen synthetic regime. This
intervention tests whether the confirmed label-noise condition transfers to
real feature geometry without claiming that either dataset has naturally known
label noise.

Datasets are Sonar (60 dimensions) and Digits (64 dimensions). For each
dataset, the standard membership split and scaling are created first. Only the
member/training labels used to form GB purity and KMeans release metadata are
flipped at a predeclared 5% or 10% rate. Candidate features, holdout samples,
membership targets, attacks, releases, and matched-k KMeans remain unchanged.

All combinations use new seeds 2, 13, 73, 314, and 808. This is a controlled
intervention on real feature distributions, not evidence of naturally occurring
label noise or a replacement for the synthetic confirmation.
