# Phase 2 — Audit: neural-representation component stability

Branch: `oush`  
Date searched: 2026-08-30  
Phase-1 artifact: `oush_neural_component_stability_phase1.md`  
Status: **KILL — local data provenance is insufficient for the frozen task**

## Audit questions

1. Is the exact fixed-structure / switched-decision / learned-representation GBC stability benchmark occupied?
2. Is neural/embedding GBC itself an open contribution class?
3. Can the local EMBER-2024 PDF and ELF cache be truthfully used as the frozen binary benchmark?

## Search protocol

Queries executed:

1. `granular ball stability partition perturbation prediction agreement decision rule`
2. `granular ball neural embedding stability classifier robustness`
3. `granular ball component benchmark radius nearest center`
4. `granular-ball classifier stability partition perturbation`
5. `EMBER 2024 malware dataset GitHub license PDF ELF train test official`
6. `FutureComputing4AI EMBER2024 GitHub license`

Only official project/dataset records, publisher pages and directly accessible papers were used for positive claims. The search interface does not expose database-wide hit totals, so this is a bounded mechanism audit, not a systematic review.

## Literature collision result

| Source family | Verified fact | Consequence |
| --- | --- | --- |
| Original GB classifier / current GBKNN line | GB classifiers use nearest-ball decisions; current papers still call mean/radius, overlap handling, classifier accuracy and run-to-run variation “stability.” | Stability language is occupied, but the located works do not establish the exact fixed-structure / changed-decision protocol. |
| Deep granular-ball representation learning | Dai et al. insert a GBC module at feature level in a deep CNN and use replay for training stability under label noise. | A neural-GB module or robustness claim would collide directly. |
| Neural / learned GB systems | GB-RVFL fuses a randomized neural network with GBs and adds a graph-embedding extension. | “GB plus neural representation” is not a novelty lever. |
| Existing repository component audit | It already separates fixed structures from nearest-centre, radius-aware and multi-centre decisions, and reports decision-dependent stability rankings. | The new line would only be independent confirmation. |

No directly matching paper was located in this bounded search that evaluates the same frozen structures under multiple decisions in both raw and frozen neural feature spaces, then jointly reports partition and prediction stability. This is `UNKNOWN`, not `CLEAR`; it does not overcome the data gate below.

## EMBER-2024 source and license verification

The [official EMBER2024 repository](https://github.com/FutureComputing4AI/EMBER2024) and [official dataset card](https://huggingface.co/datasets/joyce8/EMBER2024) describe an Apache-2.0 release, 2,568-feature vectorization, six file formats, 52 training weeks and 12 test weeks. Their PDF and ELF counts are 52,000/12,000 and 26,000/6,000 train/test rows.

The local feature-cache byte sizes match those row counts exactly:

| Local family | Inferred feature rows | Official expected rows | Result |
| --- | ---: | ---: | --- |
| PDF train / test | 52,000 / 12,000 | 52,000 / 12,000 | Size-consistent |
| ELF train / test | 26,000 / 6,000 | 26,000 / 6,000 | Size-consistent |

Each feature file has `rows × 2,568 × 8` bytes and each label file has `rows × 8` bytes, consistent with 64-bit arrays. Size consistency does not establish label semantics or source-row mapping.

## Local-label provenance preflight

| Check | Local observation | Consequence |
| --- | --- | --- |
| PDF vector labels | Values include `-1` and integers `1` through `29` in train, with a different set in test. | Not a binary `0/1` target. |
| ELF vector labels | Values include `-1` and integers through `98`. | Not a binary `0/1` target. |
| Raw JSONL records | Read-only samples contain official binary `label` values `0`/`1`, plus optional family metadata. | Raw source can support detection, but the cached vector labels describe another undocumented task. |
| Raw JSONL vs. vector rows | PDF train/test JSONL has 104,000/24,000 lines; ELF has 52,000/12,000. Each is exactly twice the corresponding vector-row count. | A selection, deduplication, pairing or label-type conversion occurred. |
| Cache metadata | Only prior GB summaries and empty vectorization logs exist. | No command, version, label type, checksum or row map binds arrays to raw JSONL. |

The official documentation says default vectorization yields malicious/benign labels, while optional label types such as `family`, `behavior`, `packer` and `group` can be requested. Because the local nonbinary arrays lack a manifest, their label type cannot safely be inferred from values. See the [official vectorization documentation](https://github.com/FutureComputing4AI/EMBER2024).

## Gate decision

```text
Neural-GB novelty: not clear; deep/embedding GB work is already occupied.
Component-benchmark novelty: UNKNOWN in this bounded audit.
Frozen EMBER binary-task provenance: FAIL.
Phase-2B empirical confirmation: DO NOT RUN.
Candidate status: KILL_NEURAL_COMPONENT_CONFIRMATION.
```

The Phase-1 protocol requires a verified binary target and row mapping. The public release is licensable and temporally structured, but the local derived arrays do not bind to that release's binary field. Treating their nonbinary labels as benign/malicious, family, or a compatible subset would be an unregistered outcome-changing choice.

Re-vectorizing raw source with the official tool and recording the version, label type, checksums, row map and a deduplication policy could create a new eligible data artifact. That is a materially larger data-preparation project and is neither necessary nor justified to rescue this low-novelty benchmark candidate. No derived data or experiment is created.

## Verified sources

1. **Joyce, R. J., Miller, G., Roth, P., Zak, R., Zaresky-Williams, E., Anderson, H., Raff, E., & Holt, J. (2025). [_EMBER2024: A benchmark dataset for holistic evaluation of malware classifiers_](https://arxiv.org/abs/2506.05074). KDD 2025.** Official repository and dataset card verify release scope, license, vectorization and time split.
2. **Dai, D., Zhu, H., Xia, S., & Wang, G. (2024). [_Granular-ball representation learning for deep CNN on learning with label noise_](https://arxiv.org/abs/2409.03254).** Feature-level GB module, CNN integration and replay-policy stability; preprint collision evidence.
3. **Sajid, M., Quadir, A., & Tanveer, M. (2024). [_GB-RVFL: Fusion of randomized neural network and granular ball computing_](https://arxiv.org/abs/2409.16735).** Neural-network/GB fusion and embedding extension; preprint collision evidence.
4. **Wang, S., Zhan, J., Xia, S., & Ding, W. (2026). Boundary-driven granular ball generation and classification via three-way decision. _Information Sciences, 755_, 123780. https://doi.org/10.1016/j.ins.2026.123780** Contemporary radius, local refinement and classification-stability work; adjacent, not an exact benchmark collision.

## Integrity note

No experiment was run. The preflight used read-only file sizes, label-value counts and three raw JSONL records; it did not execute files or alter data. No malware-efficacy, evasion, deployment or full-corpus claim is made.
