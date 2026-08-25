# Experiment

- Data: Adult, Breast Cancer, Covertype; cap 2,000.
- Clients: 5, 10, 20 with label-heterogeneous Dirichlet partitions.
- Seeds: 1, 7, 21, 42, 2026.
- Representations: raw, matched KMeans, matched MiniBatchKMeans microclusters,
  and granular balls.
- Metrics: `m/n`, accuracy drop, bytes, estimated secure additions,
  multiplications, and ciphertext count.
- Real cryptography gate: `m/n <= 0.1` and accuracy drop <= 0.02, plus a stable
  advantage over matched KMeans.

