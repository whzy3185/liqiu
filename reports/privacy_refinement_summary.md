# Privacy-Refinement Exploration Summary

## A: refinement-release membership leakage

Status: `A3_CROSS_RELEASE_VALIDATED_SYNTHETIC_ONLY`.

A reproducible conditional phenomenon was discovered and confirmed in controlled
Gaussian mixtures: high dimensionality, low redundancy, nonzero label noise,
locally heterogeneous multimodal minority structure, and fine purity refinement
produce a GB-minus-matched-KMeans membership AUC contrast. Held-out synthetic
points and seeds give a fine-refinement mean contrast of +0.078; Release 2/3
logistic contrasts exceed +0.10. A later strict shadow-to-independent-target
cross-release attack retains a mean contrast of +0.067, including a fixed-noise
control; the result is therefore not limited to same-release CV separability.

Mechanism audit attributes the highest vulnerability to small local regions and
near-centre samples. However, the synthetic result does **not** transfer to the
targeted real/natural or semi-synthetic tests: Sonar, Spambase, Digits, and
group-split Musk1 are zero or negative relative to matched KMeans. The valid
claim is therefore a controlled-distribution privacy finding, not a general
granular-ball privacy risk.

## B: GBFRS feature-selection membership leakage

Status: `KILL_B`.

The specified lianxiaoyu724 GBFRS implementation was restored from its public
RAR release and audited against FRFS, Mutual Information, and ReliefF on three
public datasets and three frozen seeds. Shadow-release-grouped membership AUC is
about 0.50 for every selector. GBFRS has lower selection stability but no
corresponding membership signal. Further B privacy mechanisms are not justified.

## Integrity record

- All discovery grids, confirmation points, seeds, matched controls, and
  negative real-transfer results are retained.
- No dataset or seed was removed after observing an outcome.
- Synthetic discovery, held-out synthetic confirmation, natural real-data tests,
  and label-noise interventions are reported as distinct evidentiary levels.
- Large ball-member trajectories are retained as compressed lossless artifacts
  where GitHub's per-file limit requires it.

## Research boundary

The next scientifically valid action is not more random benchmark hunting. A
future continuation would need either a pre-registered real data source that
independently matches the confirmed structural regime, or a reframed paper
limited to the controlled synthetic privacy mechanism and its matched-clustering
boundary. It must not turn the synthetic result into a generic deployment claim.
