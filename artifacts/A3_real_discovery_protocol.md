# A3 Strict Real-Data Discovery Protocol

The frozen Discovery pool is Dry Bean, HTRU2, and Madelon. For each outer seed,
20% of the labeled official data is an external reference subset. The remaining
80% is split into disjoint shadow and target candidate pools. The reference
subset alone fits median imputation and `StandardScaler`; neither full data nor
target candidate pool fits a transform.

Shadow and target pools are independently capped at 1,200 stratified samples
for CPU budgeting. Within each candidate pool, 50% construction membership is
selected by a clean-label-stratified split. Each setting builds six shadow
releases and five target releases. Attack fitting uses only shadow release
features and membership labels; target membership labels are used only to score
predictions. GB and matched-k KMeans share all pool, membership, transform,
threshold, release-information, and attack settings.

Outer seeds are 1, 7, and 21. Thresholds are 0.90, 0.95, and 0.99, frozen from
the strict synthetic validity protocol before any real discovery result. Release
levels are 1/2/3. Logistic Regression and Random Forest are the only attacks.

This is source/task-aware discovery: each parent UCI dataset appears once, not
as many pseudo-independent class-pair tasks. TPR@0.1% FPR is unavailable because
target pools have fewer than 1,000 negatives.
