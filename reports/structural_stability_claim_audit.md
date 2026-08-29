# Structural-Stability Claim Audit

This audit distinguishes four non-interchangeable claim types:

1. **Algorithmic determinism** — identical input and hyperparameters yield the
   same representation despite a nominal seed.
2. **Predictive robustness** — accuracy or related prediction metrics tolerate
   noise or other changed data.
3. **Structural robustness** — the granular partition itself remains similar
   for common samples after a controlled perturbation.
4. **Representation interpretability** — a ball has a human-readable geometric
   or local semantic description.

| representative source | wording/evidence located | claim type actually supported by located evidence | what it does not establish |
| --- | --- | --- | --- |
| GBC overview / original line | broad efficiency, robustness, and interpretability framing; coarse representation is said to reduce sensitivity to sample disturbance | broad methodological motivation; benchmark prediction evidence where reported | D-versus-D' common-sample partition stability or predictive/structural decoupling |
| GBG++ | “absolutely stable” generation; deterministic data-driven splitting rather than randomly selected centers; classifier benchmark comparisons | primarily algorithmic determinism; some predictive benchmark evidence | sample, label, or feature perturbation response measured by ARI/NMI/VI |
| ScOrGBG / ScOrGBC | stable centers, controlled number of balls and radii; results at 20% and 40% noisy labels with ball-count and accuracy comparisons | center-construction rationale plus predictive noise comparison | partition similarity for retained samples, fixed-test prediction agreement, or a separation of representation and decision |
| MDL-GBG / MDL-GBC | stable/interpretable granules and ARI/ACC/NMI clustering benchmarks | local construction interpretation and single-run clustering quality | perturbation stability: these ARI/NMI uses compare output to labels/ground truth, not one representation to another |

## Evidence boundary

The audit does not accuse authors of claiming a test they did not define.  A
deterministic center-selection procedure can be perfectly stable under a fixed
dataset while still having a structurally sensitive representation under a
small data perturbation.  Similarly, two models can retain accuracy while
changing predictions on a minority of test examples, or preserve those
predictions while repartitioning training samples.

The v1 cheap test and component attribution therefore assess a missing
conceptual cross-tab, not an alternative generic accuracy metric:

| dimension | v1 evidence |
| --- | --- |
| seed determinism | reported separately from data perturbation; not treated as robustness |
| partition stability | ARI, NMI, VI on retained training samples |
| predictive stability | fixed-test prediction agreement and accuracy-family metrics |
| decision sensitivity | same structures under nearest-center, radius-aware, three-center voting, and available native rule |

## Claim-audit conclusion

`CONCEPTUAL_MISMATCH_OBSERVED`.  The focused literature does not establish that
all GBC papers conflate these concepts.  It does establish that prominent
“stable” language can refer to deterministic generation, center choice,
ball-count control, or accuracy under noisy labels rather than direct
representation stability.  The repository results show why the distinction is
empirically material: structural and predictive ranks change when only the
decision component changes.

The next permitted step is an independent confirmation on pre-frozen new
datasets and new seeds.  Do not broaden the claim audit into a method-quality
ranking or introduce a new stability score.
