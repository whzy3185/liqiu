# A3 Strict Attack-Validity Decision

Decision: `A3_CROSS_RELEASE_VALIDATED` for the frozen **synthetic** regime.

The main independent-pool protocol trains attacks only on 12 shadow releases
and evaluates on eight separately generated target candidate pools. Shadow and
target pools share no samples; target membership labels are not available to
attack fitting or feature-scaling. An external reference draw fits the common
standardization. Fixed-noise controls retain one candidate pool's X, clean
labels, and noisy labels while varying only release construction membership.

| protocol | mean GB-minus-KMeans ROC-AUC | target conditions positive |
| --- | ---: | ---: |
| same-release CV diagnostic | +0.073 | -- |
| independent-pool cross-release | +0.067 | 91% |
| fixed-noise same-pool cross-release | +0.074 | -- |

For independent-pool cross-release, 74% of target conditions have a difference
at least +0.04. At threshold 0.99, Release 2/3 Logistic differences are about
+0.108--+0.110 and Random Forest differences are about +0.075--+0.076. The
mean TPR@1% FPR difference is +0.196. Each target has only 300 negative
candidates, so TPR@0.1% FPR is correctly marked unavailable rather than
interpreted.

The strict effect does not collapse relative to same-release CV, and persists
with fixed noise. Thus the previous conditional synthetic result is a valid
cross-release membership-inference phenomenon rather than only same-release
supervised separability.

This decision does not establish a real-data privacy risk. Existing real
transfer results remain negative. It only authorizes Phase 2 pre-MIA structural
diagnostics and metadata-first, source-aware dataset mining.
