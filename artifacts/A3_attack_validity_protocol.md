# A3 Strict Cross-Release Attack Protocol

The primary A3 validity result is `independent_pool_cross_release`. For every
frozen synthetic regime, twelve independent shadow candidate pools and eight
independent target candidate pools are generated from separate random draws.
Each pool has clean labels and a fixed noisy-label realization before member
selection. Construction members are a clean-label-stratified 50% sample, so
membership selection cannot determine which labels are flipped.

An external, independently generated reference draw fits `StandardScaler`; the
same published transform is used for all shadow and target releases in a
regime. It is independent of every candidate-pool membership label. GB and
matched-k KMeans use the same transformed pool, construction members, noisy
labels, release level, attack features, and attack budget.

Attack models fit only the concatenated shadow-release features and membership
labels. They are evaluated once on each target release; target membership labels
are used only after prediction to calculate metrics. `same_release_cv` is a
diagnostic comparison, never a main membership result.

The fixed-noise control uses one fixed candidate pool with fixed X, clean labels,
and noisy labels, then varies only member selection between shadow and target
releases. It tests whether a noise realization is mechanically coupled to
membership. Target and shadow candidate feature overlap is allowed only in this
explicit control; the primary protocol has no shared samples.

TPR@0.1% FPR is marked unavailable when fewer than 1,000 target negatives are
present. Logistic Regression and Random Forest are the only attack families.
