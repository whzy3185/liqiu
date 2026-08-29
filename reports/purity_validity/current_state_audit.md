# Adaptive Purity Validity Current-State Audit

Branch: `exp/granular-ball-adaptive-purity-validity`, forked from the closed
purity-contamination theory head `4f49552`.  A3 real transfer, structural
stability, and contamination-theory lines remain closed.

| generator | geometry split uses labels? | stopping uses labels? | hierarchy | fresh routing | terminal membership / majority / purity | eligibility |
| --- | --- | --- | --- | --- | --- | --- |
| `GranulationTree(kmeans)` | no: binary KMeans on X | no while growing; purity used only when cutting its maximal hierarchy | yes | exact hierarchical routing can be added from child centers | node indices / majority class / maximum empirical class fraction | primary G1 |
| `GranulationTree(class_means)` | yes: child initialization uses class means | no while growing; purity used only when cutting | yes | exact hierarchical routing can be added | same node fields | label-adaptive geometry secondary |
| `GranularBallClassifier` | indirectly: number of children equals labels in an impure ball | yes: purity terminal stop | final balls only | native terminal boundary-distance routing | ball members / majority label / empirical purity | primary G2, native routing |
| `ConfidenceBoundGranularBallClassifier` | same as clean-room GBC | yes: Wilson-bound stop | final balls only | native terminal boundary-distance routing | same fields | control only, not author method |

The structural-stability modules already expose fixed train/test splits,
preprocessing, clean-room provenance, and ball centers/radii/labels.  A3
release code exposes hierarchy metadata but must not be used as privacy
evidence.  The existing result ledger and core noise experiments record training
purity and fragmentation, but none supplies the required independent
fresh-routing reliability target.

Only the first two implementations can furnish `EXACT_HIERARCHICAL_ROUTING`
after retaining child centers on the frozen maximal tree.  The two clean-room
GBC implementations provide `NATIVE_TERMINAL_ROUTING`; any nearest-center
variant is explicitly `APPROX_NEAREST_CENTER_ROUTING` and cannot be primary
population-ball evidence.
