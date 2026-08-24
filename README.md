# Automated Research Lab for Granular and Uncertainty-Aware AI

This repository is an evidence-first research system for granular computing,
granular-ball computing (GBC), rough sets, three-way decisions (3WD), and their
intersections with uncertainty-aware machine learning and agents.

The repository deliberately starts without a proposed new algorithm. Work must
follow this order:

1. map the literature and occupied mechanisms;
2. reproduce representative baselines;
3. discover reproducible failure regions;
4. propose mechanisms tied to an observed failure;
5. run novelty and cheap-test gates;
6. retain negative results and attack every survivor.

## Reproducibility contract

- Experiments are launched from JSON configuration files.
- Stochastic experiments use seeds from `1, 7, 21, 42, 2026` during initial
  exploration; decisive claims must add more seeds.
- Every run appends one immutable JSON object to
  `experiments/results/experiments.jsonl`.
- Every record contains the current Git commit (and dirty state), configuration
  hash, runtime, peak memory, metrics, structure statistics, outcome, and notes.
- `exploration` and `confirmation` datasets are separated. A confirmation run
  requires an explicit rationale and refuses hyperparameter search.
- Failed runs are data. They are appended with `outcome: failure` and are never
  silently deleted.

## Quick start

```bash
python3 -m experiments.runners.run_experiment \
  --config experiments/configs/smoke.json
python3 scripts/check_task0.py
```

Use a temporary output during development:

```bash
python3 -m experiments.runners.run_experiment \
  --config experiments/configs/smoke.json \
  --output /tmp/research-smoke.jsonl
```

## Current phase

TASK 0 infrastructure is established. TASK 1–2 populate the literature map and
component matrix. Baseline implementations and counterexample search begin only
after enough primary sources have been mapped to choose representative methods.

