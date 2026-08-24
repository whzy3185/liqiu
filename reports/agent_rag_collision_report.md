# Agent/RAG collision gate — 2026-08-24

## Multi-granularity memory/RAG

### Search result

No exact title-level `granular-ball RAG` paper was found, but the problem/mechanism
space is already crowded:

- UAMG-RAG: uncertainty-guided adaptive multi-granularity retrieval and
  re-retrieval (2026 preprint, 10.21203/rs.3.rs-10020935/v1).
- MG2-RAG: multi-granularity graph for multimodal RAG (arXiv:2604.04969).
- Multi-granularity evidence retrieval for verifiable multimodal RAG
  (Findings ACL 2026, 10.18653/V1/2026.FINDINGS-ACL.509).
- MGK-RAG: multi-granularity knowledge-guided retrieval for radiology
  (10.1145/3774904.3792924).

### Gate decision

`HIGH_COLLISION` for generic coarse-to-fine, uncertainty-adaptive or hierarchical
retrieval. Replacing hierarchical clustering with granular-ball vocabulary is
explicitly rejected. This route may reopen only after a demonstrated
granular-specific property (risk/coverage/cost guarantee or failure repair) that
these systems cannot provide.

## Three-way Agent decision

### Search result

Exact `three-way decision Agent` titles were not found, but adjacent mechanisms
are mature: uncertainty-adaptive retrieval, value-of-information human–agent
communication, context-aware tool filtering, selective/abstaining prediction,
and agent tool-use benchmarks. Three-way decision theory itself has learnability,
geometry, sequential and cost-sensitive variants.

### Gate decision

`PARTIAL_COLLISION`, no implementation. ACT/INVESTIGATE/ABSTAIN labels alone are
not a mechanism. Reopening requires a predeclared uncertainty estimator, action
loss matrix, information cost, and a theorem or failure region not reducible to
standard VOI/selective prediction.

## Priority

Neither route enters survivors. Collision screening is complete; experimental
systems are intentionally not built.
