# A3 Conditional-Regime Confirmation

The frozen high-dimensional, low-redundancy, nonzero-noise regime was tested on
four held-out nearby parameter points and five new seeds per point. None of the
20 dataset/seed units reused discovery seeds.

At fine refinement (`purity >= 0.90`), mean GB-minus-matched-KMeans AUC is
`+0.0780` across all releases and attacks. Every held-out dataset/seed unit has
a positive mean contrast; 16 of 20 exceed +0.05. Release-specific confirmation
is also positive:

| release | attack | mean GB-minus-KMeans AUC |
| --- | --- | ---: |
| Release 1 | Logistic | +0.0785 |
| Release 1 | Random Forest | +0.0468 |
| Release 2 | Logistic | +0.1043 |
| Release 2 | Random Forest | +0.0664 |
| Release 3 | Logistic | +0.1037 |
| Release 3 | Random Forest | +0.0683 |

The four held-out parameter points have mean contrasts from +0.0609 to +0.0962.
This confirms the frozen conditional claim in synthetic data: fine granular-ball
refinement can expose more membership signal than a matched-k KMeans summary in
locally heterogeneous, high-dimensional, low-redundancy mixtures with nonzero
label noise.

This is not a general granular-ball privacy claim. The next required test is
targeted real-data confirmation selected by the frozen structural condition.
