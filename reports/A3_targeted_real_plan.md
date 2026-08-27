# A3 Targeted Real-Data Plan

The synthetic confirmation freezes a high-dimensional, low-redundancy,
nonzero-noise regime. No public benchmark is assumed to meet every latent
condition exactly, so real data are classified by structural relevance and
confounds rather than post-hoc attack results.

Initial CPU-feasible exploratory targets are Sonar and Spambase, both obtained
from the official UCI source. Sonar provides small-n, 60-dimensional physical
signals; Spambase provides a much larger 57-dimensional heterogeneous real
collection with a documented concept boundary. They are exploratory real-data
tests, not substitutes for synthetic confirmation.

Musk1 is intentionally deferred: rows are multiple conformations of molecules,
so a row-random split could create group leakage. Arcene and Madelon are also
deferred, despite their high dimension, because both are probe/redundancy-heavy
feature-selection benchmarks and need their official predefined split parsers.

All candidates and their decisions are retained in
[A3_targeted_real_registry.csv](A3_targeted_real_registry.csv). Every included
dataset uses the same A3 release/attack/control pipeline and five frozen seeds.
