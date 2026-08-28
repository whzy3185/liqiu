# A3 Internet Advertisements Strict Discovery v1

Internet Advertisements entered Discovery as a pre-specified high-fragmentation,
low-conflict near-boundary control.  The complete strict independent
reference/shadow/target protocol produced 540 unique rows: three outer seeds,
three thresholds, three release levels, six shadow releases, five target
releases, matched-k KMeans, and both attack families.  No seed, threshold, or
release level was removed.

| metric | mean GB - KMeans | standard deviation | positive fraction | fraction at least +0.04 |
| --- | ---: | ---: | ---: | ---: |
| ROC-AUC | -0.0075 | 0.0223 | 0.400 | 0.011 |
| PR-AUC | -0.0048 | 0.0186 | 0.404 | 0.004 |
| TPR at 1% FPR | +0.0013 | 0.0145 | 0.507 | 0.026 |

The ΔAUC seed means are -0.0064, +0.0015, and -0.0174.  The small positive
mean at seed 7 is not a reproducible effect and is retained with the two
negative seeds.  Fine GB structure remains present (mean ball count 30.3,
34.2, and 36.4 at 0.90, 0.95, and 0.99; small-ball ratios 0.284, 0.297, and
0.308), but it does not translate into a material GB-specific leakage contrast.

Decision: `INTERNET_ADS_DISCOVERY_V1_NEGATIVE_FOR_MATERIAL_GB_SPECIFIC_EFFECT`.
This is a negative near-boundary control, not evidence for a new selection
rule.  Complete results are retained in
`results/A3_internet_ads_discovery.csv`.
