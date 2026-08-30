# Phase 1 — AD-GBC cross-domain dense-prediction transfer

Branch: `oush`  
Status: **SCOPED — requires source, code and dataset-license audit**  
Date: 2026-08-30

## Decision context

Classical GB application roles, fixed radius decisions, and an earlier
AD-GBC-inspired missing-view module are closed. The repository application map
records one distinct, source-available path: **AD-GBC**, a differentiable
anisotropic granular-ball module inside a segmentation network, has official MIT
code but is evaluated in medical image segmentation only. This candidate is a
strict transfer/replication study of that existing module in a small,
non-medical pixel-label setting.

It makes no method, geometry, segmentation, anomaly-detection or industrial-AI
novelty claim. Its possible contribution is a reproducible answer to the narrow
application question: do AD-GBC's learned region semantics survive a transfer to
an industrial defect mask task after strong same-budget controls?

## Research Question Brief

### Primary question

On one small, license-verifiable industrial visual-defect segmentation dataset,
does the unchanged AD-GBC region module improve held-out pixel-mask performance
and calibration over the same UNet backbone without the module, while retaining
its advantage under a matched learnable isotropic-prototype ablation?

### FINER assessment

| Criterion | Score | Reason |
| --- | ---: | --- |
| Feasible | 3/5 | The local Apple M5 has Metal support; feasibility still depends on author-code executability and a small licensed target dataset. |
| Interesting | 3/5 | Tests a documented domain boundary of an accepted learnable GB module. |
| Novel | 2/5 | A cross-domain transfer is not a new algorithm and dense segmentation already has GB work. |
| Ethical | 5/5 | Static public industrial images; no human subjects, deployment decisions or security payloads. |
| Relevant | 3/5 | A clear positive or negative transfer result can delimit a claimed semantic-region benefit. |
| **Average** | **3.2/5** | Only a replication/transfer artifact is plausible. |

### Scope boundaries

**In scope**

- The authors' unchanged AD-GBC module and its documented dependencies, only if
  the official repository is licensed and executable.
- One small public industrial defect dataset with pixel-level masks, a clear
  research-use license and a fixed official or documented split. `KolektorSDD2`
  is the discovery target only; it is not yet accepted into the protocol.
- A compact UNet backbone; original resolution and augmentation may follow the
  author release only after being recorded before the target test set is read.
- Apple MPS execution, with a strict single-device cap of 3 wall-clock hours per
  run and 24 total training runs.

**Out of scope**

- Any altered centre, scale, membership, loss, attention, decoder or split rule.
- Adding a novel GB component, pretraining on an external image corpus, or
  claiming generic anomaly detection, factory deployment, safety certification
  or performance beyond the named target dataset.
- Choosing another target dataset after seeing test metrics.

## Methodology blueprint

### Preflight gates

Before data download or training, verify all four:

1. The AD-GBC repository is author-owned, MIT licensed, installable on the
   current MPS/PyTorch environment, and contains a runnable segmentation entry
   point or enough source to reproduce one without inventing module details.
2. The candidate industrial dataset has a redistributable/research-use license,
   pixel masks and a documented split or a reproducible, preregistered split.
3. The target task is semantic/defect mask segmentation, not merely image-level
   anomaly classification.
4. A 10-image forward/backward smoke run fits MPS memory and finishes within
   five minutes. Failure of any preflight item is `KILL_ADGBC_TRANSFER`.

### Frozen experimental conditions

After the preflight passes, freeze one target dataset and run three seeds
`1, 7, 21` under a single budget schedule. Every model sees exactly the same
train/validation/test images, preprocessing, augmentations, optimizer, learning
rate schedule, epoch cap and early-stopping rule.

| Arm | Trainable components | Attribution purpose |
| --- | --- | --- |
| A: Backbone | compact UNet only | Strong no-GB reference |
| B: Isotropic control | same insertion point and region count; scalar learned scale | Tests whether anisotropy, not merely prototypes/parameters, matters |
| C: AD-GBC | unchanged author module | Existing-method transfer arm |

Parameter counts, MPS peak allocated memory, epoch time, total wall time and
the exact commit/environment are mandatory outputs. If the author module cannot
be inserted at an identical stage, the design is invalid rather than silently
approximated.

### Metrics and decision rule

Primary metric: foreground Dice on the frozen test masks. Secondary metrics:
foreground IoU, pixel AUPRC, Brier score and expected calibration error. Report
per-image values and bootstrap 95% confidence intervals, but make no
significance claim from a single dataset.

The transfer signal is descriptive only unless all conditions hold:

1. Across all three seeds, C exceeds A by at least 2 Dice points and B by at
   least 1 Dice point in the mean test Dice.
2. C does not worsen pixel AUPRC or Brier score by more than 1 point versus A.
3. C's median wall time and peak MPS memory are no more than 1.5 times A.
4. The same ordering occurs on validation before it is inspected on test.

Any failure is `KILL_ADGBC_TRANSFER`. Passing permits only: “the published
AD-GBC module transferred under this bounded industrial mask protocol.” It does
not establish a new module or a general industrial-segmentation claim.

## Devil's-advocate checkpoint 1

### Verdict: REVISE BEFORE PHASE 2

1. **Replication-not-novelty risk (major).** A one-dataset transfer can at most
   be a reproducibility/application artifact. The manuscript framing must not
   call it a new GBC method.
2. **Control asymmetry (major).** A generic UNet comparison alone is inadequate;
   the matched isotropic control is mandatory to attribute anisotropic GB
   geometry rather than extra learnable capacity.
3. **Dataset shopping risk (major).** The discovery target must be accepted or
   rejected by license/mask/split criteria before any metric is generated.
4. **Resource fragility (minor).** MPS compatibility must be observed, not
   inferred from GPU availability.

### Strongest counter-argument

“This merely ports an existing segmentation module to another image collection;
it supplies neither a method nor broad evidence.”

That criticism is accepted as the default. The only defensible product is a
fully reproducible, negative-or-positive boundary result. If the author code or
data cannot support that standard, the candidate closes before training.

## Phase-2 audit protocol

Verify: AD-GBC paper/repository identity and license; code installation and MPS
requirements; the target dataset's license, masks, split, size and access path;
and whether an accepted prior work already transfers AD-GBC to industrial defect
mask segmentation. The protocol must record every unresolved dependency and may
not download data or run training before the audit verdict.
