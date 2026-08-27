# A3 Musk1 Group-Aware Targeted Results

Musk1 was evaluated with a molecule-group-disjoint member/holdout split: no
molecule can appear in both sets, and molecule/conformation names were excluded
from the 166 numeric features. Natural labels and frozen 5%/10% member-training
label interventions each used five new seeds, matched-k KMeans, all releases,
and both attacks.

| training label condition | fine-refinement mean GB-minus-KMeans AUC |
| --- | ---: |
| natural | -0.0324 |
| 5% intervention | -0.0332 |
| 10% intervention | -0.0315 |

Every molecule-group seed average is negative. This is strong targeted negative
evidence: high-dimensional local conformational structure and controlled label
noise alone do not transfer the confirmed Gaussian-mixture regime to Musk1.
The group split prevents a same-molecule cross-split artifact from producing a
spurious membership signal.
