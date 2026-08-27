# A3 Small-Ball and Boundary Audit

This audit reruns the frozen synthetic confirmation points at thresholds 0.90,
0.95, and 0.99 using Release 3 and the logistic membership attack. Candidate
rows are assigned to their nearest released ball; ball size, purity, radius,
refinement depth, and normalized centre distance are recorded exactly as
observable from the release.

| ball-size bin | GB AUC mean | matched-KMeans AUC mean | paired GB-minus-KMeans AUC |
| --- | ---: | ---: | ---: |
| 1--2 | 0.950 | 0.889 | +0.091 (18 comparable units) |
| 3--5 | 0.956 | 0.925 | +0.058 (4 comparable units) |
| 6--10 | 0.930 | 0.893 | +0.033 (20 comparable units) |
| 11--20 | 0.861 | 0.852 | +0.014 (35 comparable units) |
| >20 | 0.719 | 0.699 | +0.025 (49 comparable units) |

Both release families show more attack signal for smaller local regions. The
GB-specific excess is largest in size 1--2, but its variability is high because
only 18 runs contain both GB and KMeans candidates in that bin. It is therefore
mechanistic support for the synthetic conditional effect, not independent proof
of a universal small-ball rule.

For GB candidates with nonzero radius (`n=30,646`), a standardized linear model
of attack score has `R²=0.630`. Normalized distance has the strongest coefficient
(-0.210) and Spearman association (-0.719): candidates nearer a ball centre are
more vulnerable. Refinement depth also has a negative Spearman association
(-0.441). Radius is positively associated with score (Spearman +0.492), whereas
purity is weak in this correlated regression. These are descriptive structural
associations, not causal effects.

Raw candidate data, bin metrics, and regression coefficients are saved in:

- `results/A3_mechanism_candidates.csv`
- `results/A3_small_ball_metrics.csv`
- `results/A3_mechanism_regression.csv`
