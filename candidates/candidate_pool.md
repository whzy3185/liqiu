# Candidate pool

Candidates are admitted only after an observed failure and a novelty check. Each
entry links mechanism, failure evidence, closest work, cheapest decisive test,
and scoring inputs.

## H-003 mechanism pool (generation stage)

All mechanisms target the observed global-purity incompatibility. None is a
retained paper topic. Scores are 0–5; collision is dangerous when high.

| ID | Candidate mechanism | Direct failure target | Cheapest decisive test | N | E | Depth | Cost | Theory | Gen | Pub | Agent | Collision | Weighted score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M01 | Binomial/Beta lower-confidence-bound purity stop | small balls appear pure by chance; global p phase changes | REJECTED: 15-run Cheap Test worsens explosion/over-refinement | 2 | 5 | 2 | 5 | 3 | 3 | 2 | 2 | 3 | 27 |
| M02 | Cross-fitted local risk + granule-cost stop | accuracy-neutral explosion and harmful refinement | reserve folds inside each candidate region; accept split only on risk-cost gain | 4 | 5 | 4 | 4 | 3 | 5 | 5 | 3 | 2 | 42 |
| M03 | Bootstrap/perturbation stability stop | seed-sensitive structure and unstable refinement | resample members and reject unstable child assignments | 3 | 5 | 4 | 3 | 4 | 5 | 4 | 3 | 3 | 37 |
| M04 | Calibration-aware split/stop | purity confidence is uncalibrated on Electricity/Ionosphere | split only when held-out Brier/ECE improves under cost constraint | 4 | 4 | 4 | 4 | 3 | 5 | 5 | 3 | 1 | 42 |
| M05 | Local MDL code-length stop | hundreds of low-value balls | REJECTED: direct 2026 MDL-GBC collision | 1 | 5 | 5 | 4 | 5 | 5 | 2 | 2 | 5 | 30 |
| M06 | Pareto risk–balls–calibration frontier | no scalar purity suits all regimes | retain nondominated local actions then select by budget | 3 | 5 | 3 | 4 | 3 | 5 | 4 | 3 | 3 | 35 |
| M07 | Sequential probability-ratio split test | abrupt Phoneme phase transition | accumulate split evidence until accept/reject boundary | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 2 | 1 | 41 |
| M08 | Value-of-information split | many splits add negligible accuracy | expected risk reduction divided by compute/granule cost | 4 | 4 | 4 | 3 | 4 | 5 | 5 | 5 | 2 | 42 |
| M09 | Local out-of-bag error stopping | training purity blind to test error | bootstrap candidate split and use OOB loss | 3 | 5 | 3 | 3 | 2 | 4 | 4 | 3 | 2 | 34 |
| M10 | Split-then-merge validation | irreversible over-refinement | validate local merge after each refinement wave | 2 | 4 | 3 | 3 | 2 | 4 | 3 | 2 | 3 | 26 |
| M11 | Multi-scale prediction ensemble | threshold selection unstable | average predictions over purity path with complexity weights | 3 | 4 | 3 | 3 | 3 | 4 | 4 | 2 | 3 | 30 |
| M12 | Change-point detection on purity–cost curve | phase transitions | stop at first statistically supported diminishing-return point | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 3 | 1 | 45 |
| M13 | Local intrinsic-dimension-conditioned stop | heterogeneous regions need different scale | regress split gain on local dimension and sample count | 3 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 3 | 31 |
| M14 | Boundary-mixing-conditioned stop | interleaved boundary failure | estimate cross-label neighbor edges inside each ball | 3 | 5 | 4 | 4 | 4 | 5 | 4 | 3 | 2 | 40 |
| M15 | Label-noise posterior purity correction | high p chases noisy labels | infer local noise rate before purity calculation | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 2 | 3 | 33 |
| M16 | Conformal local miscoverage stop | fixed p lacks risk meaning | refine until local prediction-set coverage target is met | 4 | 3 | 5 | 3 | 5 | 5 | 5 | 3 | 2 | 41 |
| M17 | Bayesian hierarchical local purity | sparse balls overfit purity | partial-pool region purities across hierarchy | 4 | 4 | 5 | 2 | 5 | 5 | 5 | 2 | 2 | 41 |
| M18 | Contextual bandit over split/keep/merge | actions vary by local state | offline contextual bandit on recorded split trajectories | 3 | 4 | 4 | 2 | 2 | 4 | 4 | 5 | 3 | 33 |
| M19 | Minimum-size confidence schedule | tiny pure balls explode | purity threshold rises with effective sample size | 2 | 5 | 2 | 5 | 3 | 4 | 3 | 2 | 3 | 29 |
| M20 | Region-specific validation budget allocation | expensive tests needed only near boundary | allocate resampling budget by uncertainty/VOI | 4 | 4 | 4 | 3 | 3 | 5 | 4 | 5 | 2 | 40 |

N = novelty estimate before full gate. Weighted score follows the project rule;
scores are triage judgments and do not override collision evidence.

## First implementation queue

M05 is rejected after a direct collision; M01 is rejected after its Cheap Test.
M12, M04, M02, M08 and M16 form the revised deep-search queue.
