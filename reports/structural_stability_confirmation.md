# Structural Stability Confirmation v1

The pre-frozen confirmation used three datasets not in the structural-stability
Discovery set (Iris, Sonar, Spambase), a new train/test split seed, three new
perturbation seeds, four explicitly-labelled repository implementations, and
two unchanged mild perturbations.  All 72 rows completed without duplicates.

The confirmation criterion was at least four prediction-agreement >=0.95 and
ARI <=0.70 cases spanning at least two datasets and two generators.  It does
not pass.  There is exactly one qualifying row: Sonar, 1% sample deletion,
seed 911, `gbc_confidence_bound_control`, ARI 0.5069 and prediction agreement
0.9808.  No second dataset or generator confirms it.

| dataset | perturbation | mean ARI | mean prediction agreement | mean absolute accuracy change |
| --- | --- | ---: | ---: | ---: |
| Iris | 5% label flip | 0.8153 | 0.9496 | 0.0329 |
| Iris | 1% sample deletion | 0.9299 | 0.9781 | 0.0175 |
| Sonar | 5% label flip | 0.8456 | 0.9247 | 0.0433 |
| Sonar | 1% sample deletion | 0.5683 | 0.9151 | 0.0304 |
| Spambase | 5% label flip | 0.8140 | 0.9080 | 0.0230 |
| Spambase | 1% sample deletion | 0.6197 | 0.8795 | 0.0212 |

The Discovery finding is retained as an implementation- and dataset-conditional
observation.  It is not a confirmed multi-generator structural-stability
regime.  No perturbation severity, dataset, metric, or seed will be altered to
rescue the result.
