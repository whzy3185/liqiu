# A3 Semi-Synthetic Real-Feature Intervention Results

The frozen member-training-label-noise intervention was completed on Sonar and
Digits at 5% and 10% noise with five new seeds, all releases, attacks, and
matched-k KMeans controls.

| real feature set | training label noise | fine-refinement GB-minus-KMeans AUC |
| --- | ---: | ---: |
| Sonar | 5% | +0.004 |
| Sonar | 10% | +0.011 |
| Digits | 5% | -0.083 |
| Digits | 10% | -0.056 |

Sonar is near zero and seed-inconsistent; Digits is negative in every seed.
Thus the confirmed synthetic regime does not transfer under this intervention to
either tested real feature geometry. These results remain explicit negative
evidence, not a reason to modify the synthetic hypothesis after the fact.

This intervention is controlled semi-synthetic evidence only: it does not claim
natural label noise in either source. It motivates one further structurally
matched candidate, Musk1, whose multiple conformations require a group-aware
molecule split to avoid duplicate-group leakage.
