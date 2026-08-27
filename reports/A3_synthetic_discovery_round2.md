# A3 Synthetic Regime Discovery: Round 2

Round 2 froze the high-density, multimodal minority background identified as
least-negative in round 1 and scanned dimension {20, 80}, redundant-feature
fraction {0.0, 0.8}, and label noise {0.0, 0.10} on new seeds 42, 99, and 2026.

The full 1,440-row record reveals a conditional GB-specific contrast. At 80
dimensions with no redundant feature block and 10% label noise, mean
GB-minus-matched-KMeans AUC is +0.069 across all thresholds, releases, attacks,
and new seeds. Under high refinement, the contrast is larger: at threshold 0.99
with Release 2/3 and a logistic attack, it is approximately +0.123 to +0.124.
The three seed mean has standard deviation below 0.02 in the strongest cell.

The same broad condition without label noise has a weaker positive average
(+0.042), while 20-dimensional and high-redundancy conditions are negative on
average. This is a discovery result, not confirmation. It defines the frozen
candidate: high-dimensional, low-redundancy, locally heterogeneous mixtures
with nonzero label noise and fine refinement.

All 24 parameter/seed units, including negative regimes, are retained in
`results/A3_synthetic_round2_raw.csv`; associated ball trajectories and
manifests are retained alongside it.
