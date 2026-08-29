# Stability Generator Reproduction Audit

The initial cheap test uses four existing repository implementations with
explicit provenance rather than claiming four paper-faithful author-code
reproductions.

| generator id | implementation | provenance | fixed construction | first-round status |
| --- | --- | --- | --- | --- |
| `tree_kmeans_binary` | `GranulationTree(split_method="kmeans")` | repository clean-room | recursive binary KMeans, purity cut 0.85 | include |
| `tree_class_means_binary` | `GranulationTree(split_method="class_means")` | repository clean-room | recursive class-mean initialized binary split, purity cut 0.85 | include |
| `gbc_multiclass_cleanroom` | `GranularBallClassifier` | clean-room structure-audited against original GBC smoke | split an impure ball into the number of labels, purity 0.85 | include |
| `gbc_confidence_bound_control` | `ConfidenceBoundGranularBallClassifier` | existing internal cheap-test control | same multiway split with one-sided Wilson stop | include as a stop-rule control, never as author reproduction |

All methods will be evaluated with common nearest-center prediction, not their
native boundary-distance rule.  The native rule is outside the first cheap-test
primary comparison and will only be considered after a GO decision.  GBG++ and
LDGBG remain unavailable and are recorded as such rather than approximated.
