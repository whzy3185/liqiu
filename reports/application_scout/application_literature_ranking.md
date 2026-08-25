# Application Literature Ranking

## Scoring

Each field uses 1 (low) to 5 (high). `Recent crowding` and `reproduction
difficulty` are costs; the opportunity score reverses them:

`mean(6-crowding, value, data, ML fit, GB evidence, gain space, paper potential, 6-difficulty)`.

| Domain | Recent crowding | Application value | Public-data breadth | Conventional-ML fit | Existing GB evidence | Gain space | Paper potential | Reproduction difficulty | Opportunity score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Industrial fault | 4 | 5 | 5 | 5 | 4 | 3 | 4 | 3 | 3.88 |
| Credit risk / fraud | 1 | 5 | 5 | 5 | 1 | 5 | 4 | 3 | 4.12 |
| IIoT intrusion | 3 | 5 | 4 | 5 | 3 | 2 | 3 | 4 | 3.38 |
| Medical diagnosis | 4 | 5 | 4 | 4 | 3 | 2 | 3 | 4 | 3.12 |

## Interpretation

The numerical opportunity score puts finance first because direct GB collisions
are nearly absent. It does **not** make finance the first experiment: there is
little direct evidence that GB raises strong credit/fraud models.

Industrial fault diagnosis remains the primary line because it combines:

- several independent real sensor datasets;
- clear difficult regimes where local reliability can matter;
- direct recent positive GB evidence;
- strong compatibility with classical signal features and tree ensembles;
- an application narrative that does not require a new deep architecture.

Its risk is crowding. The project must avoid reproducing MgBIF label correction,
WGBRS feature selection, or GDNN end-to-end embedding. The initial mechanism is
restricted to cross-fitted structural features and reliability weights added to
strong conventional models.

Finance is the backup with the largest novelty space. It advances only if
GB features or weights improve PR-AUC/MCC on at least three independent tasks.

IIoT receives a higher GO threshold because the 2026 GBIFS paper directly covers
six intrusion datasets. Medical is deferred due to direct GB-RVFL/GB-RGTSVM
collisions and harder patient/image protocols.

## Ranked execution order

1. **Industrial fault diagnosis** -- primary evidence-seeking line.
2. **Credit risk / fraud** -- novelty-rich backup.
3. **IIoT intrusion** -- rapid high-bar screen.
4. **Medical diagnosis** -- deferred backup.

## Prompt-1 decision

`GO` to dataset inventory and leakage-safe pipeline construction. No algorithm
performance claim is authorized by this literature stage.

