# Experiment

- Cloud sizes: 10,000 and 100,000 blocks.
- Seeds: 1, 7, 21, 42, 2026.
- Corruption: uniform, clustered, hot-targeted, cold-targeted, and policy-aware
  adversarial.
- Controls: uniform, weighted random, direct risk score, anomaly score, matched
  KMeans groups, matched tree leaves, and GB center-only.
- GB methods: group empirical risk and group risk plus three-way sampling tiers.
- Budgets: 50/100/250 and 100/500/1000 for the two cloud sizes.
- Metrics: detection probability, time to first detection, corrupted-block
  recall, audit cost, and 95th-percentile miss rate.

