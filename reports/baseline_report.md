# Baseline report

## Status

The first author-code audit covers seven core GBC/3WD entries plus one optional
clustering comparator. Two generation variants have passed a structure smoke
test. No paper-level result has yet been claimed reproduced.

| Baseline | Paper | Upstream | License | Current result |
|---|---|---|---|---|
| Original GBC generation | 10.1016/j.ins.2019.01.010 | `syxiaa/GBC@5986bea` | no license | structure smoke passed |
| Adaptive GBG | 10.1109/tnnls.2022.3203381 | `syxiaa/GBC@5986bea` | no license | structure smoke passed |
| GBG++ | 10.1109/tetci.2024.3359091 | no public repository found | unknown | code search pending |
| Local-density GBG | 10.1016/j.ins.2025.122295 | no public repository found | unknown | code search pending |
| GBRS | 10.1109/tnnls.2023.3325199 | `syxiaa/GBRS@e7d92e7` | no license | source/artifacts audited |
| GBFRS | 10.1016/j.knosys.2023.110898 | `AldrinLake/GBFRS@25a8bc2` | MIT | source audited |
| 3WC-GBNRS++ | 10.1109/tfuzz.2024.3397697 | `xiaodiaolingyun/3WCGBNRS-@085dfa7` | no license | source/supplement audited |
| S3WD-GBRS | 10.1109/tfuzz.2025.3536564 | `xiaodiaolingyun/S3WD-GBRS@48d1938` | no license | source/supplement audited |

Exact URLs and commits are machine-readable in `baselines/upstream_registry.csv`.

## Smoke-test evidence

Both tests used 300 generated moon samples, noise 0.12, and seed 42. They load
the exact author-code commit without copying it into this repository.

| Experiment ID | Variant | Balls | Mean size | Resubstitution accuracy | Wall time |
|---|---|---:|---:|---:|---:|
| `20260824T095642Z-9b06be41c5e4` | original purity split | 6 | 50.00 | 0.9867 | 73.762 s |
| `20260824T095755Z-aa2b5e62ddf0` | adaptive split/overlap | 11 | 27.27 | 1.0000 | 0.825 s |

These accuracies are nearest-center predictions on the same data used to build
the balls; they test structural usability only. The original run's wall time
includes one-time Matplotlib font-cache construction, so the times are not a
valid algorithm comparison.

## Reproducibility findings

- The author GBC repository explicitly maps `gb_origin.py` and
  `gb_adaptive_upload.py` to the relevant generation work, but has no license.
- The original file assumes binary labels for its purity function and fixes
  k-means `random_state=5`; adapters must document these constraints.
- The adaptive file uses random center initialization and overlap-driven further
  splitting. The adapter fixes the configured seed.
- The 3WC and S3WD repositories contain scripts and supplementary PDFs but no
  package metadata, README, or license. Their experiment entry points assume
  local data files and require normalization into the common interface.
- The MIT-licensed GBFRS repository is reusable, but its main path includes GUI
  and multiprocessing concerns; core functions should be isolated before tests.
- The optional `GB-DP` clone transferred at least 15 MB without completing in
  two minutes and was stopped. It is not a substitute for the local-density GBG
  paper, which addresses generation for classification rather than density-peak
  clustering.

## Next decisive work

1. Wrap GBRS, GBFRS, and one 3WD method on small public/synthetic inputs.
2. Separate cold-import overhead from fit/predict runtime.
3. Search supplementary and author pages for GBG++ and local-density GBG code;
   otherwise produce paper-faithful clean-room implementations with deviations
   logged.
4. Add KNN, SVM, random forest, AdaBoost, KMeans, and DBSCAN under the same split
   and preprocessing protocol.
