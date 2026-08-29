# Structural-Stability Literature Collision Audit

Status: `NO_DIRECT_SYSTEMATIC_COLLISION_FOUND_IN_FOCUSED_AUDIT`.

This is a focused collision gate, not a claim of exhaustive literature
coverage.  Searches covered granular-ball stability, structural/partition
stability, perturbation, consistency, robustness, interpretability, and the
named GBG/GBG++/LDGBG/ACCGBG/ScOrGBG/MDL families.  The existing repository
literature registry and current publisher/preprint records were checked.

| method/family | stated stability or robustness evidence | direct partition comparison under data perturbation? | predictive-vs-structural decoupling? | audit consequence |
| --- | --- | --- | --- | --- |
| original GBC / GBG | robustness and classification claims in the foundational line | not located in scoped sources | not located | include only audited clean-room baseline |
| GBG++ | claims absolute generation stability and reports classifier comparisons | no ARI/NMI/VI data-perturbation protocol located | no | direct conceptual claim target, not a reproduced generator |
| ScOrGBG / ScOrGBC | stable centers, controlled ball count/radii and noisy-label accuracy comparisons | no partition-similarity protocol located | no | direct conceptual claim target, not a reproduced generator |
| LDGBG / ACCGBG | adaptive/efficiency/robustness generation claims | no systematic common-sample partition audit located | no | implementation unavailable for v1 |
| MDL-GBG / MDL-GBC | interpretable local model-selection and benchmark ARI/ACC/NMI against labels | ARI/NMI are clustering-quality metrics, not D-versus-D' structure similarity | no | recent adjacent work; no equivalence to the proposed test |

The collision distinction is essential: published ARI/NMI commonly compare a
single generated clustering to ground truth, whereas the cheap test compares
two granular partitions of the same retained training samples after a small
controlled perturbation, then compares their fixed-test predictions.  No scoped
source was found to systematically combine multiple GBC generators, sample /
label / feature perturbations, established partition-similarity metrics, and
fixed-test prediction agreement.

The direction may proceed to the v1 cheap test.  It must not claim that words
such as “stable,” “robust,” or “interpretable” in earlier papers mean structural
stability; the subsequent claim audit must distinguish algorithmic determinism,
predictive robustness, and representation stability.
