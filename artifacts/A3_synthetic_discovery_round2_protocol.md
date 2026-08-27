# A3 Synthetic Discovery: Frozen Round-2 Expansion

Round 1 found strong GB refinement leakage but no materially positive
GB-minus-matched-KMeans contrast. The least-negative context was high
separation, high minority density ratio, a 30% minority, and three local
minority modes. Round 2 fixes those four conditions and explores three
previously unscanned structural axes:

- ambient dimension: 20 or 80;
- redundant-feature fraction: 0.0 or 0.8;
- label noise: 0.0 or 0.10.

This yields eight parameter points. Each is evaluated on new seeds 42, 99, and
2026 with the same thresholds, releases, attacks, and matched-k KMeans control.
No threshold, release, attack, or seed will be selected after execution.

Round 2 is still discovery. A candidate regime requires a materially positive
GB-minus-KMeans contrast across new seeds and multiple releases/attacks before
any real-data confirmation set can be defined.
