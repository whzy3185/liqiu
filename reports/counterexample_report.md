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

Evidence status: **deprecated for official-classifier claims**. These runs used
nearest-center prediction after author-code granulation. Audit of `gb_knn.py`
showed the official classifier minimizes center distance minus mean radius. V1
remains useful as a downstream-sensitivity record but must not support GBC
classifier conclusions; corrected v2 is required.

Corrected XOR v2 completed 140/140 runs. At overlap 0.25, original and adaptive
both have mean gap −0.038 and 65/70 individual runs are negative. The effect
survives faithful classification but is roughly half the v1 estimate.

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

## Alternating-label independent generators

Evidence status: **deprecated for official-classifier claims** for the same
nearest-center discrepancy. Generator contrasts remain descriptive only until v2.

Corrected alternating v2 completed 90/90 runs. Sector wheels remain negative in
29/30 method/seed runs; corrected mean gaps range −0.031 to −0.058. Gaussian XOR
still ties at compact settings, and checkerboard-6 remains counterevidence.

Alternating v1 completed 90/90 runs using five seeds and three generator
families. Mean held-out gaps versus the best RF/RBF-SVM/5-NN reference are:

| Case | Original gap | Adaptive gap | Interpretation |
|---|---:|---:|---|
| Gaussian XOR σ=0.10 | 0.000 | 0.000 | compact disconnected regions solved |
| Gaussian XOR σ=0.25 | 0.000 | 0.000 | compact disconnected regions solved |
| Gaussian XOR σ=0.40 | −0.003 | −0.021 | only small degradation |
| Checkerboard-4 | −0.053 | −0.077 | common replication |
| Sector wheel-4 | −0.047 | −0.070 | common replication |
| Sector wheel-8 | −0.068 | −0.088 | common replication |
| Sector wheel-12 | −0.056 | −0.088 | common replication |

This narrows the observation: disconnected same-class regions are not sufficient,
and ambient dimension is not the cause. Locally interleaved/curved boundaries
with label mixing inside local balls are plausible, while checkerboard-6 prevents
a simple monotonic “more alternation is worse” claim.

## Mechanism-signal audit

Across the 230 corrected-v2 targeted runs, sample-weighted training ball impurity
correlates only moderately with held-out gap (Pearson −0.30; original −0.42).
Granule count/mean-size correlations shrink to −0.22/+0.32, weakening the v1
fragmentation story. These remain observational and generator-confounded.

The sharper negative result is that original GBC has zero samples below its
configured 0.85 purity threshold in all 115 targeted runs, including runs with a
−0.16 held-out gap. Thus satisfying the purity stopping rule does not diagnose
the observed out-of-sample failure. Boundary stability and fragmentation need
direct stress tests before a repair mechanism is proposed.

## Public real data and purity sensitivity

Five public OpenML datasets × five seeds all trail the best RF/RBF-SVM/5-NN
reference at fixed purity 0.85. Mean gaps range from −0.047 (Banknote) to −0.240
(Ionosphere). Electricity generates ~1637 balls from 3500 training samples and
ECE 0.25; Ionosphere has only ~16 balls yet similarly poor calibration, so
fragmentation is not a universal explanation.

A separate 105-run purity scan exposes incompatible regimes:

| Dataset | Key transition | Interpretation |
|---|---|---|
| Phoneme | p=.70: 1 ball/Acc .707 → p=.80: ~412 balls/Acc .848 | under-splitting phase change |
| Electricity | p=.80: ~1277 balls/Acc .696 → p=1: ~1999/Acc .698 | accuracy-neutral explosion |
| Ionosphere | p=.80: ~6.7 balls/Acc .770 → p=1: ~71.7/Acc .723 | harmful over-refinement |
| Banknote | p=1 reaches Acc 1.000 | high purity beneficial |
| Sonar | p≈.95–1 best | high purity beneficial but many small balls |

O-004/PH-003 therefore concern a global-rule incompatibility, not a claim that
high or low purity is universally preferable. Cross-method replication remains
mandatory.

The author accelerated-GB method then completed the same 105-run scan. It
reproduces Phoneme's one-ball→hundreds-of-balls transition and Electricity's
accuracy-neutral explosion. Dataset-specific best thresholds remain incompatible,
although the exact Ionosphere/Sonar optima move with the generator. PH-003 is
therefore promoted to H-003 as a cross-method, cross-real-dataset hypothesis.
This promotes the problem—not “adaptive purity” or any other proposed solution.

## Next experiment

Measure within-ball label mixing, boundary error and curvature/scale mismatch,
and repeat with a clean-room GBC implementation. Seek a real-data analogue before
any mechanism proposal. Continue reporting absolute gaps; use loss ratio only
when reference loss exceeds a declared floor.
