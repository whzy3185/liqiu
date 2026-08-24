# Hypotheses

Hypotheses remain falsifiable and specify affected method family, data region,
observable outcome, competing explanation, and decisive experiment.

## Refuted PH-001 — high-dimensional XOR degradation

Targeted replication rejects ambient dimension as the primary driver. Accuracy
gaps do not worsen monotonically from d=2 to d=500.

- Affected family: purity-split original GBC and adaptive split/overlap GBG.
- Proposed region: XOR-like disconnected alternating labels after random
  projection into high ambient dimension.
- Observable: negative held-out accuracy gap under shared preprocessing.
- Competing explanations: RF-specific advantage, one projection, generator
  artifact, untuned purity, and distance concentration.
- Decisive experiment: completed as XOR v1 (140 runs).

## Pre-hypothesis PH-002 — locally interleaved boundary weakness

Original and adaptive spherical GBC may systematically lose locally interleaved
or curved alternating boundaries when mixed labels fall inside the same local
balls; ambient dimension and disconnected class regions alone are insufficient.

- Evidence region: XOR overlap 0.25 across dimensions 2–500 and five seeds.
- Observable: negative held-out accuracy gap against best RF/RBF-SVM/5-NN.
- Corrected strength: with author boundary-distance classification, 65/70
  overlap-0.25 XOR runs are negative; sector wheels reproduce in 29/30 runs.
- Independent support: continuous XOR overlap, checkerboard-4, and sector wheels
  with 4/8/12 sectors.
- Counterexamples: Gaussian XOR with well-separated compact clusters is solved;
  checkerboard-6 does not degrade original GBC.
- Missing: real-data analogue, clean-room method, and a mechanism measure
  connecting within-ball mixed labels/boundary curvature to error.
- Status: cross-method and cross-generator replicated observation under faithful
  author prediction, still not a
  research hypothesis because the causal statistic is unresolved.

## Pre-hypothesis PH-003 — global purity creates incompatible local regimes

A single global purity stopping threshold cannot simultaneously avoid
under-granulation, accuracy-neutral granule explosion, and harmful over-refinement
across heterogeneous data regions/datasets.

- Evidence: 105 real-data runs, five OpenML datasets, three seeds, seven purity
  levels.
- Observable regimes: Phoneme under-splitting phase transition; Electricity
  accuracy-neutral explosion; Ionosphere harmful over-refinement.
- Counterpoint: Banknote benefits nearly monotonically from greater purity.
- Status: cross-dataset replicated for original GBC, not yet cross-method.
- Decisive next test: adaptive/GBG++/local-density generators and local-region
  diagnostics under the same accuracy–granule-count objective.
