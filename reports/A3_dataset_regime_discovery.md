# A3 Strict Real Discovery: Pool v1

The frozen v1 pool comprised three independent parent datasets selected before
any real A3 outcome: Dry Bean (high structural-interest), HTRU2 (high
fragmentation but low-conflict boundary control), and Madelon (external
synthetic negative control). Each parent task used strict independent
reference/shadow/target pools, three outer seeds, three fine thresholds, three
release levels, both attacks, matched-k KMeans, and no task was removed.

| source task | task-level mean ΔAUC (GB - KMeans) | task-level mean ΔPR-AUC | task-level mean ΔTPR@1%FPR | positive ΔAUC fraction |
| --- | ---: | ---: | ---: | ---: |
| Madelon | +0.001 | +0.001 | +0.015 | 0.981 |
| HTRU2 | -0.023 | -0.012 | +0.004 | 0.133 |
| Dry Bean | -0.099 | -0.074 | -0.022 | 0.000 |

Source-level and task-level summaries are identical here because each source
contributes one task. Madelon is numerically near a tie, not a material positive
effect. HTRU2 turns increasingly negative at 0.99 despite its 977× structural
fragmentation ratio. Dry Bean is negative across every outer seed, threshold,
release, and attack. Thus neither fragmentation nor the v1 geometry-label
conflict metric alone predicts a real positive regime.

No `A3_selection_rule_v1` is created: there is no positive/neutral/negative
structural separation on which to freeze one. Results in
`results/A3_real_discovery.csv` are retained in full. This pool alone does not
yet satisfy the broad source-diverse discovery condition for `KILL_A`; the
metadata-first catalog is extended before further MIA only through source and
pre-MIA hard-filter information.

## MicroMass group-disjoint extension

The frozen metadata extension then admitted UCI MicroMass pure spectra under a
separate strain-disjoint protocol.  Its 540 complete rows give mean ΔAUC
+0.0053 (standard deviation 0.0364), with only 14.4% of combinations reaching
+0.04 and seed-level means -0.0028, +0.0150, and +0.0036.  This is another
negative result for a material real GB-specific effect, not a candidate for
seed selection or confirmation.  The detailed protocol and full result are in
`artifacts/A3_micromass_group_discovery_protocol.json` and
`reports/A3_micromass_group_discovery.md`.
