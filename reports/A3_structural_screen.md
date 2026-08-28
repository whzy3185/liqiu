# A3 Structural Profile and Pre-MIA GB Probe

All metrics use the frozen v1 definition in
`artifacts/A3_structural_metrics_v1.json`. Full labeled official train/validation
data are used only for structural screening. No member/nonmember split, attack
feature, score, ROC-AUC, PR-AUC, or privacy statistic was calculated.

| source task | n × d | effective-rank ratio | conflict mean | k10 disagreement | 0.99/0.70 fragmentation | 0.99 size≤2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Madelon | 2,600 × 500 | 0.863 | 0.137 | 0.366 | 2.16× | 0.908 |
| Arcene | 200 × 10,000 | 0.006 | 0.087 | 0.230 | 4.14× | 0.782 |
| HTRU2 | 17,898 × 8 | 0.462 | 0.013 | 0.018 | 977× | 0.573 |
| Dry Bean | 13,611 × 16 | 0.216 | 0.061 | 0.072 | 303× | 0.706 |

The table is deliberately not reduced to a weighted A-score. Arcene is excluded
after the hard filter because its 200 labeled rows cannot support a credible
independent reference/shadow/target membership protocol. Dry Bean, HTRU2, and
Madelon form the frozen Discovery pool: respectively high structural interest,
low-conflict near-boundary control, and external synthetic negative control.

All data came from verified UCI CC-BY archives. SHA-256 and archive test status
are in `artifacts/A3_approved_downloads.json`; the raw pre-MIA profiles and
probes are in `results/dataset_structural_profiles.csv` and
`results/dataset_gb_structure_probes.csv`.
