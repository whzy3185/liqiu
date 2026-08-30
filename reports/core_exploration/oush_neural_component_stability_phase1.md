# Phase 1 — Neural-representation component-stability confirmation

Branch: `oush`  
Status: **SCOPED — requires Phase-2 literature confirmation**  
Date: 2026-08-30

## Rationale and non-claim

All current GB algorithm and application routes are closed. One narrow P1 artifact
claim remains: the existing component-controlled audit found that a granular
representation's structural stability, fixed-test predictive stability, and
decision-rule stability can disagree. It has not been independently checked on a
modern learned feature space or a realistic, high-dimensional security corpus.

This is a **reproduction/measurement** candidate, not a new granulation, radius,
neural-network, security, privacy, or compression method. In particular, prior
local EMBER runs retained every training sample while using 2.2–2.8 GB peak
memory, so no efficiency claim is allowed.

## Research Question Brief

### Primary question

When the same granular-ball structures are evaluated under multiple fixed
decision rules, does the separation between structural stability and predictive
stability reproduce on local EMBER-2024 PDF and ELF feature corpora in both
standardized raw features and a frozen MLP penultimate-layer representation?

### FINER assessment

| Criterion | Score | Reason |
| --- | ---: | --- |
| Feasible | 4/5 | Local PDF and ELF matrices have 2,568 features and fixed train/test files; the bounded protocol avoids the observed full-run memory cost. |
| Interesting | 3/5 | Tests whether an existing stability distinction survives learned representations rather than only small tabular data. |
| Novel | 2/5 | It may be ordinary model/partition stability measurement. Its only possible value is a rigorously controlled GBC benchmark/reproduction artifact. |
| Ethical | 4/5 | Local malware features only; no execution or generation of malware. Dataset license/provenance must be verified before dissemination. |
| Relevant | 4/5 | It establishes which stability statements can be made about GBC components in a security-classification setting. |
| **Average** | **3.4/5** | Proceed only as a literature-first artifact audit. |

### Scope

**In scope**

- The existing clean-room `GranulationTree(kmeans)`, `GranulationTree(class_means)`,
  original-style clean-room GBC, and confidence-bound GBC control; none may be
  labelled author code.
- Local EMBER-2024 PDF and ELF train/test matrices, after a data-provenance
  preflight verifies shape, labels, class support, and train/test chronology or
  explicitly records chronology as unavailable.
- Two prespecified feature spaces: train-only standardized raw features and a
  frozen two-hidden-layer MLP penultimate embedding. The MLP is fitted once on
  the unperturbed training portion; its encoder is then frozen for every paired
  GB perturbation.
- Existing decisions only: nearest centre, native/radius-aware distance where
  available, and three-centre inverse-distance vote.

**Out of scope**

- Claiming that an MLP+GB hybrid improves malware detection, compression,
  robustness, calibration, privacy, adversarial security or temporal adaptation.
- Tuning the encoder, GB purity, decision rule, subsample, threshold or
  perturbation after test results are visible.
- Running files, binaries, or payloads; these are static feature matrices only.

## Methodology blueprint

### Data and resource preflight

The repository cache identifies the local PDF and ELF matrices as 2,568-feature
EMBER-2024 data. The preflight must verify that fact from matrix and label files,
record their dtypes/shapes and class counts, and document the dataset license/source.
It must also confirm whether the supplied split is chronological from acquisition
metadata. If chronology cannot be verified, all output must say **provided
train/test split**, not temporal generalization.

Use a frozen, stratified cap of 2,000 train and 2,000 test samples per corpus,
chosen before fitting; the same indexed samples are used by all methods. The cap
is an execution safeguard, not evidence about the full corpus. Stop a run and
record `RESOURCE_STOP` if it exceeds 45 minutes CPU wall time or 6 GB peak RSS;
do not lower the cap after seeing any metric.

### Paired intervention

For each corpus × feature space × generator:

1. Fit the structure to the frozen baseline training subset.
2. Refit it after each predeclared training-only perturbation: 1% sample
   deletion, 1% label flip, and Gaussian feature noise with standard deviation
   0.01 in the relevant frozen feature space.
3. Hold the corresponding feature transform/encoder and test set fixed within
   each pair. Predict from the **same fitted structure** with each eligible
   decision rule.

Run seeds `1, 7, 21, 42, 2026`; all data perturbations reuse the seed list.
There are no seed searches and no selection of a worst-case perturbation.

### Measurements

For two structures on their shared training samples, report ARI, NMI and VI.
For each decision rule on the identical test points, report prediction agreement,
accuracy, balanced accuracy and macro-F1. For each fixed corpus/space/
perturbation/seed cell, rank GB generators independently by ARI and prediction
agreement, and compare those rankings across decisions.

The MLP's own test accuracy is reported only as representation provenance. It is
not a comparator that GB must beat, and no GB result may be attributed to
neural-network performance.

### Confirmation and kill gates

This candidate is a confirmatory artifact only if Phase 2 finds no existing
component-controlled GBC benchmark that already performs the same structure/
decision/learned-representation separation.

The empirical confirmation gate then requires all of the following:

1. On each corpus and in both feature spaces, at least two of the three
   perturbations contain at least four of five seeds with `ARI <= 0.70` and
   prediction agreement `>= 0.95` under one prespecified nearest-centre rule.
2. In both feature spaces, changing only the decision rule alters the
   generator-ranking order in at least 30% of eligible paired cells, measured by
   a nonzero pairwise ranking reversal rate against nearest centre.
3. The directional finding is present in **both** PDF and ELF; one corpus or one
   feature space alone is descriptive and fails the confirmation gate.
4. The same-partition nearest-centre control must explain neither the full
   decision sensitivity nor the structural-predictive separation. If it does,
   report a generic partition-stability result and KILL the GB-specific
   benchmark claim.

Failure of any condition is `KILL_NEURAL_COMPONENT_CONFIRMATION`. Passing does
not establish a new GB algorithm; it permits only a reproducibility/benchmark
paper about component reporting.

## Devil's-advocate checkpoint 1

### Verdict: REVISE BEFORE PHASE 2

1. **Generic stability collision (major).** Partition and prediction stability
   are established evaluation ideas. The literature audit must find whether the
   exact same component-controlled GBC protocol already exists; a vague absence
   of titles is insufficient.
2. **Encoder confounding (major).** Refitting an encoder for every perturbation
   would turn representation drift into GB drift. The encoder must be frozen
   once, trained only on the baseline training subset, and never access test
   labels.
3. **Security overclaim (major).** Static EMBER features do not support claims
   about operational malware execution, evasion resistance, or detection
   deployment. The scope prohibits them.
4. **Small-capped sample generalization (minor).** A 2,000-row cap is justified
   for a controlled audit but cannot represent full-corpus performance.

### Strongest counter-argument

“This repeats ordinary clustering/decision sensitivity on a neural embedding;
the GB label adds no scientific insight.”

The only surviving reply would be evidence that prominent GBC stability claims
leave the fixed-structure/changed-decision distinction untested, plus an
independent two-corpus reproduction that is not explained by the nearest-centre
control. Otherwise the correct outcome is KILL.

## Phase-2 audit protocol

Search and verify primary sources for:

1. `granular ball stability partition perturbation prediction agreement decision rule`;
2. `granular ball neural embedding stability classifier robustness`;
3. `granular ball component benchmark radius nearest center`;
4. `cluster stability prediction stability representation stability neural embeddings`;
5. `EMBER 2024 dataset feature release license train test`.

The audit must separately answer: (a) whether the component-controlled GB
benchmark is occupied; (b) whether neural/embedding GB stability is occupied;
and (c) whether the locally cached EMBER use is licensable and accurately
described. A failure on (c) removes EMBER from this candidate rather than
silently substituting another dataset.

## Integrity note

No experiment has been run and no `data/` file has been modified. The three
untracked pre-existing result/data paths remain excluded from this work.
