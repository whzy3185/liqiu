# Accepted-paper map edge exploration, round 4

Date: 2026-08-25.

| Candidate | Runs | Decision |
|---|---:|---|
| Inference-time missing-view recovery | 12 | `REJECT` fixed GB mechanism |
| Model failure-slice discovery | 12 | `REJECT` |

Fixed GB region means do not recover cross-view semantics as well as Ridge/kNN.
GB audit slices do not concentrate independent-test errors as well as KMeans or
kNN error density.

The next candidate changes mechanism class: a learnable anisotropic region
module inspired by AD-GBC will be tested for cross-view recovery under the same
small single-device budget. It is not a retry of fixed splitting; centers,
scales, memberships and missing-view prototypes are optimized jointly.
