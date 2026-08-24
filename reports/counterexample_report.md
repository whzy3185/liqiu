# Counterexample report

## Campaign v1

The first bounded random search completed 72/72 runs: 12 parameter regions × two author GBC generators × seeds 1/7/21. Random forest used the identical train/test split and scaling. This is exploration-pool evidence only.

| Trial | Family | d | Original gap | Adaptive gap | Original failure ratio | Adaptive failure ratio |
|---:|---|---:|---:|---:|---:|---:|
| 000 | gaussian_blobs | 100 | +0.008 | -0.008 | 0.96 | 1.03 |
| 001 | moons | 100 | -0.047 | +0.019 | 2.07 | 0.65 |
| 002 | circles | 20 | -0.058 | -0.017 | 1.25 | 1.08 |
| 003 | xor | 100 | -0.069 | -0.050 | 1.46 | 1.33 |
| 004 | checkerboard | 2 | -0.022 | -0.003 | 1.09 | 1.02 |
| 005 | spirals | 5 | -0.058 | -0.050 | 1.15 | 1.13 |
| 006 | thin_manifold | 20 | -0.011 | -0.008 | 1.23 | 1.18 |
| 007 | nested_clusters | 5 | -0.033 | +0.006 | 1.19 | 0.98 |
| 008 | anisotropic | 2 | -0.069 | -0.014 | 3.55 | 1.57 |
| 009 | multimodal_class | 100 | +0.006 | +0.008 | 3.17 | 0.39 |
| 010 | varying_density | 2 | -0.067 | -0.042 | 1.25 | 1.16 |
| 011 | imbalanced_density | 2 | +0.006 | -0.086 | 0.96 | 1.87 |

## Observations, not hypotheses

1. **Common high-dimensional XOR weakness (replication candidate).** At d=100, both original and adaptive GBC trail the reference across the three-seed aggregate: gaps −0.069 and −0.050; failure ratios 1.46 and 1.33. This is the clearest common signal in v1, but it still needs new XOR generators and more seeds.
2. **Original-specific high-dimensional moons weakness.** Original trails by −0.047 with failure ratio 2.07, while adaptive leads by +0.019. This argues against calling curved manifolds a family-wide failure from this campaign.
3. **Adaptive-specific imbalanced-density weakness.** Adaptive trails by −0.086 while original is roughly tied (+0.006). Random-center/overlap behavior is a candidate explanation, not yet evidence.
4. **Spirals and varying density show smaller common gaps.** Both methods trail on these trials, but failure ratios are only 1.13–1.25 and one parameter draw is insufficient.
5. **The ratio objective is unstable near a perfect reference.** Multimodal trial 009 produces an original mean failure ratio 3.17 even though mean accuracy is 0.997 and mean gap is positive. Future ranking must combine absolute gap and a denominator floor; ratio alone can manufacture a dramatic 'failure'.

## Promotion decision

No entry is promoted to a research hypothesis. High-dimensional XOR advances to targeted replication. Moons and imbalanced-density signals advance as method-specific red-team cases. Trial 009 is primarily a metric counterexample.

## XOR targeted replication v1

The decisive grid completed 140/140 runs over dimensions 2/5/10/20/50/100/500,
overlaps 0.05/0.25, five seeds, and both original/adaptive author methods. Each
run compares against RF, RBF-SVM, and 5-NN and uses the best reference accuracy.

| Overlap | Original mean gap | Adaptive mean gap | Negative individual gaps |
|---:|---:|---:|---:|
| 0.05 | −0.025 | −0.035 | 62/70 |
| 0.25 | −0.090 | −0.069 | 69/70 |

The original high-dimensional explanation is refuted: d=500 is not
systematically worse than d=2 and the dimension curve is non-monotonic. Overlap,
not ambient dimension, is the stable control in this grid. O-001 is upgraded to
a cross-method replicated observation, but it remains within one synthetic
family and is not promoted to a research hypothesis.

## Next experiment

Construct independent alternating-label generators (rotated/multi-cell XOR and
controlled checkerboards), measure within-ball label mixing and boundary error,
and repeat with a clean-room GBC implementation. Seek a real-data analogue before
any mechanism proposal. Continue reporting absolute gaps; use loss ratio only
when reference loss exceeds a declared floor.
