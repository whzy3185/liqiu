# A3 Targeted Real-Data Exploratory Results

Sonar and Spambase were selected before outcome analysis as CPU-feasible public
numeric targets adjacent to the synthetic regime. Five frozen seeds, all
thresholds/releases/attacks, and matched-k KMeans were completed.

| dataset | fine-refinement mean GB-minus-KMeans AUC | seed-level pattern | interpretation |
| --- | ---: | --- | --- |
| Sonar | -0.007 | mixed, near zero | no GB-specific contrast |
| Spambase | -0.056 | negative in every seed | matched KMeans explains or exceeds leakage |

The earlier Breast Cancer pipeline benchmark is also negative (-0.099) and is
retained. These real-data findings do not invalidate the confirmed synthetic
conditional regime; nor do they supply direct natural-data support for it.
Neither Sonar nor Spambase has a verified match to the regime's nonzero label
noise and high-dimensional low-redundancy condition.

The results are exploratory and negative. They remain in
`results/A3_refinement_raw.csv` with all ball trajectories. Any next real-data
test must be explicitly designated as a controlled semi-synthetic intervention
if training-label noise is introduced.
