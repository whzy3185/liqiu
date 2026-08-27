# B0 Decision

Decision: `KILL_B`.

The predeclared cheap-test conditions show GBFRS membership ROC-AUC at random
level. None of the three public datasets, three seeds, releases, or two attack
models provides evidence that selection output reveals membership. Traditional
feature-selection controls are similarly near random, so there is no
GB-specific privacy profile to explain or protect.

Do not add datasets, tune GBFRS parameters, invent a feature-selection privacy
metric, or study output perturbation under this branch. The documented lower
selection stability of GBFRS is retained as a descriptive result only; it is
not sufficient to claim membership leakage.
