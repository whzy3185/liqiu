# B0 Cheap-Test Protocol

The official lianxiaoyu724 GBFRS smoke preflight used 24 shadows on Breast
Cancer seed 1. It is retained separately. The resource-adaptive formal cheap
test uses 12 shadows per dataset/seed, which still permits a shadow-grouped
five-fold attack evaluation while reducing repeated official selection cost.

Datasets and frozen seeds are Breast Cancer, Sonar, and Spambase with seeds 1,
7, and 21. Each run holds an independent 20% reference set, caps the shadow
candidate pool at 600 via a stratified pre-split, then creates 12 stratified
half-pool shadow selection datasets. Candidate order/ID is never an attack
feature; attack folds are grouped by shadow release.

The methods are official GBFRS, FRFS, MI, and ReliefF. FRFS/MI/ReliefF use the
same selected-feature count as each GBFRS shadow output. Every method gets its
natural release types only. A future extension to five seeds or 24 shadows is
triggered by a materially non-random discovery signal, not by a single best
seed.
