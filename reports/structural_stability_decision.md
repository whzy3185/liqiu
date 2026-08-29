# Structural Stability Decision

Decision: `KILL_STRUCTURAL_STABILITY`.

The v1 cheap test found real decoupling examples and a decision-rule-sensitive
ranking, so it correctly triggered a bounded component audit and an independent
confirmation.  However, the pre-frozen confirmation does not reproduce the
required cross-dataset, cross-generator decoupling: one isolated internal-
control row is insufficient.

Consequently, the repository must not promote a paper claim that granular
representation stability generally decouples from predictive stability.  It
also must not expand data search, perturbation severity, seed count, new
stability metrics, theory, or author-method comparisons to recover a positive
story.  The valid retained artifact is narrower: stability claims should
distinguish algorithmic determinism, representation stability, predictive
agreement, and decision-rule sensitivity.

The A3 synthetic finding remains separate and synthetic-only; the A3
real-transfer kill remains in force.
