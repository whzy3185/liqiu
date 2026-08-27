# A3 Synthetic Regime Discovery: Round 1

The discovery grid fixed 16 Gaussian-mixture structures before analysis:
separation {0.75, 2.0}, density ratio {1, 5}, minority fraction {0.10, 0.30},
and minority local modes {1, 3}. All runs used 600 rows, 20 dimensions, 50%
redundant features, 2% label noise, three seeds (1, 7, 21), five refinement
thresholds, three releases, two attacks, and mandatory matched-k KMeans.

The retained raw record has 2,880 attack rows and 72,036 ball records. Across
all synthetic configurations, GB membership AUC increased strongly from the
coarsest to finest refinement in every seed/release/attack trajectory. However,
the mean GB-minus-KMeans AUC contrast was negative in every full structural
group in this first grid. The largest positive subgroup average was only about
0.034, below the predeclared practically material 0.05 contrast.

This round therefore supports a **refinement leakage phenomenon** but does not
yet establish a granular-ball-specific component. It is neither a universal
claim nor an A-line KILL. The next exploratory expansion is frozen before it is
run: it holds a high-density, multimodal minority condition and scans ambient
dimension, redundant-feature fraction, and label noise to test whether those
structural factors alter the GB-versus-KMeans contrast.

All raw rows, including negative conditions, remain in
`results/A3_synthetic_raw.csv`; the manifest and ball trajectories preserve the
full discovery history.
