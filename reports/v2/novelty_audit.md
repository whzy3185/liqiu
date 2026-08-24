# V2 novelty audit

## Theory line

- Claim: global purity has stable Pareto regret on heterogeneous GBC trees.
- Evidence: 240 synthetic configs, two tree generators, four families.
- Negative evidence: cut selection is strongly equivalent to tree pruning/SRM;
  known-region routing and test oracle are upper-bound conveniences.
- Closest literature: CART/cost-complexity, optimal pruning, adaptive partitions,
  classification-aware quantization, rate-distortion, MDL-GBC.
- Collision risk: HIGH standalone.
- Decision: P1 application explanation.
- Next kill test: GNN frontier audit and GBC-specific lower-bound attempt.

## Federated line

- Claim: client-specific prototype budgets may beat uniform allocation under a
  global communication budget.
- Evidence: Uniform→observed-oracle gap ≈1.12 pp across all Digits α settings.
- Negative evidence: validation F5 fails equal-byte and equal-risk gates; server
  model choice changes conclusions; only Digits was run.
- Closest literature: FedProto (10.1609/AAAI.V36I8.20819), global prototype
  distillation for heterogeneous FL (10.1038/S41598-024-62908-0), prototype
  similarity distillation (10.1109/TKDE.2024.3386712), adaptive client/gradient
  compression (10.1109/INFOCOM53939.2023.10229029), rate-constrained FL
  quantization (10.1109/ICASSP49660.2025.10889213), and 2026 granular-ball
  federated open-intent representation (10.1016/J.NEUNET.2026.108817).
- Collision risk: HIGH for prototype compression; UNKNOWN/MEDIUM for explicit
  global-byte/client-specific task-risk allocation.
- Decision: `P1_PROBLEM_METHOD_REJECTED`; do not run MNIST/Fashion-MNIST.
- Next kill test: none until a value estimator is proposed independently of
  validation client accuracy and pre-clears FedProto/adaptive-compression work.
