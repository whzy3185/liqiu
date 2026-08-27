# Regime Search Protocol

This project seeks a reproducible conditional phenomenon, not an average win on
all tabular datasets. Discovery scans controlled synthetic distributions before
targeted real-data confirmation.

## Discovery axes

- class separation and overlap;
- density ratio and minority fraction;
- number of local modes and minority islands;
- noise, redundant feature blocks, and ambient dimension;
- observed refinement structure: ball count, small-ball fraction, singleton
  fraction, purity distribution, radius dispersion, and refinement depth.

Every synthetic parameter point, seed, release level, attack, GB result, and
matched-k KMeans result is retained. No point is removed after seeing attack
performance.

## Confirmation gate

A candidate regime must state its condition before confirmation. Confirmation
uses new synthetic seeds, held-out nearby parameter combinations, and real
datasets selected by the frozen structural condition. A conditional finding is
eligible to continue only if its effect remains material, repeated, and not
fully reproduced by matched KMeans or small-group controls.

An aggregate weak result across unrelated datasets is not itself a KILL. A
failure to identify any stable regime after this discovery and confirmation
cycle is the KILL condition.
