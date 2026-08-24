# Theory Track — H-003 global-purity incompatibility

## Proposition 1: no globally compatible purity threshold

### Assumptions

Let binary labels satisfy `P(Y=0)=q>1/2`. A purity-split GBC stops a ball when
its empirical majority proportion is at least `τ`; otherwise a two-means split
is attempted. Prediction uses the majority label of the selected ball.

Consider two distributions with the same root class proportion:

1. `D_sep`: the two classes occupy two sufficiently separated compact clusters,
   so the first two-means split recovers the classes.
2. `D_null`: `X` is continuous and independent of `Y`.

### Claim

- For `D_sep`, `τ≤q` stops at the root and has accuracy `q`; `τ>q` splits into
  two pure balls and has accuracy 1 (under exact empirical root proportion q).
- For `D_null`, no feature-based classifier can exceed Bayes accuracy `q`. For
  any `τ≥q+ε`, the probability that empirical purity stops at the root is at
  most a Hoeffding tail of order `2 exp(-2nε²)`.
- Therefore no global `τ` both realizes the beneficial split on `D_sep` and
  avoids statistically unnecessary refinement on `D_null`.

### Proof sketch

The first statement follows directly from the stop rule and the separability
assumption. Under independence, the conditional label distribution is constant,
so Bayes predicts the majority class everywhere. The empirical majority count is
a binomial deviation around q; Hoeffding bounds the event that it reaches a
threshold above q. Thresholds at or below q fail to split `D_sep`, while
thresholds above q trigger `D_null` with probability approaching one.

### Counterexample boundary

The claim does not say every high threshold is harmful: on `D_sep` it is
necessary and optimal. It also does not prove the exact number of descendant
balls under `D_null`; that depends on the recursive splitter. The 40-run
verification records the observed explosion for the clean-room author-consistent
implementation.

## Proposition 2: distribution-free local validation is sample hungry

### Assumptions

For a candidate split, let paired validation loss difference `Z∈[-1,1]` have
mean improvement `Δ>0`. A sequential controller wants a two-sided confidence
radius smaller than Δ with error probability at most δ.

### Claim

A Hoeffding-style certificate requires, in the worst case,

`m ≥ 2 log(2/δ) / Δ²`

validation observations. For `Δ=0.02, δ=0.1`, this is about 14,979 observations.

### Proof sketch

Apply Hoeffding to the empirical mean of bounded paired differences:
`P(|mean(Z)-Δ|≥r)≤2 exp(-m r²/2)`, then solve with `r=Δ`.

### Consequence

Local balls contain far fewer observations than whole datasets. This explains
why Candidate 2 consumed all validation data without acting and why local
cross-fit pruning lost fine structure. Variance-adaptive or structural
assumptions may improve the bound, but distribution-free local adaptation cannot
be assumed cheap.

## Lemma candidate: honest purity reliability

For a fixed, independently evaluated ball with `m` labels and true majority
probability p, empirical purity has the usual concentration error. For M fixed
balls, a union bound introduces `log(M/δ)`. The current GBC balls are selected on
the same labels used to report purity, so the fixed-ball bound is not directly
valid. An honest sample, selective-inference correction, or explicit partition
complexity term is required.

This lemma is not yet proved for adaptively generated granular-ball trees.

## Empirical verification

Forty configuration-recorded runs use q=0.7, n=1000 training points, 2000 test
points, thresholds 0.6/0.7/0.8/0.9 and five seeds.

- `D_sep`: 1 ball/Accuracy .7 at τ≤.7; 2 balls/Accuracy 1 at τ>.7.
- `D_null`: 1 ball/Accuracy .7 at τ≤.7; roughly 422–675 balls and Accuracy
  .582–.630 at τ>.7.

The experiment verifies the construction; it is not a substitute for the proof.
