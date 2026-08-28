# A3 MicroMass Strain-Disjoint Discovery v1

MicroMass was admitted through the frozen pre-MIA gate as a source-complete
extension, not because of an attack result.  The experiment uses only the 571
pure-reference spectra for 20-species classification.  All 360 mixture spectra
are excluded.  Reference, shadow, and target pools are disjoint by bacterial
strain, and every release separately assigns membership by strain.  External
reference-only preprocessing, matched-k KMeans, three outer seeds, three
thresholds, three release levels, six shadow releases, five target releases,
and both attacks were all retained.

The full output has 540 rows with no duplicate rows.  The primary GB-minus-KMeans
contrast is weak and unstable:

| metric | mean delta | standard deviation | positive fraction | fraction at least +0.04 |
| --- | ---: | ---: | ---: | ---: |
| ROC-AUC | +0.0053 | 0.0364 | 0.600 | 0.144 |
| PR-AUC | +0.0051 | 0.0338 | 0.522 | 0.111 |
| TPR at 1% FPR | +0.0015 | 0.0536 | 0.478 | 0.233 |

The outer-seed mean ΔAUC values are -0.0028 (seed 1), +0.0150 (seed 7), and
+0.0036 (seed 21).  Thus the one somewhat positive seed is not retained as a
privileged result.  Across the complete grid, ΔAUC ranges from -0.1420 to
+0.0933.  The strongest threshold-level structural observation is also not an
effect: GB has about 32 balls and 93.7% small (size <=2) balls at every tested
fine threshold, so 0.90/0.95/0.99 do not form a meaningful refinement
trajectory in these small strain-disjoint member sets.

Decision: `MICROMASS_GROUP_DISCOVERY_V1_NEGATIVE_FOR_MATERIAL_GB_SPECIFIC_EFFECT`.
This additional high-dimensional, high-local-disagreement dataset does not
yield a real positive regime or justify an A3 selection rule.  It reinforces
the existing synthetic-only boundary rather than testing a post-hoc favourable
seed.  Complete rows are retained in
`results/A3_micromass_group_discovery.csv`.
