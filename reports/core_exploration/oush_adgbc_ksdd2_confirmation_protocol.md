# AD-GBC × KSDD2 confirmation protocol

Branch: `oush`  
Status: **FROZEN FOR EXTERNAL-RUNNER SMOKE; no full result yet**  
Date: 2026-08-31

## Scope and evidence boundary

This is a bounded transfer reproduction of existing methods, not a new
granular-ball or industrial-segmentation method. It uses the official KSDD2
train/test release and two official MIT repositories:

- AD-GBC, commit `25abdcae0947c893320a344eda20b9606abbc79e`;
- Rolling-Unet, commit `8a43d40c218917e454c0584a853757e3a2cf9c80`.

The author trainers randomly split one data directory; they cannot use KSDD2's
official train/test division directly. A separate, versioned external runner is
therefore required. It must import the pinned architectures unchanged, record
all adapter logic, and never be described as author code.

## Frozen dataset protocol

| Partition | Records | Rule |
| --- | ---: | --- |
| Official train | 2,331 image/mask pairs | Exclude only the duplicate names containing ` (copy)` found in the archive. |
| Internal validation | Stratified 20% of official train, per seed | Stratify by whether the mask contains any foreground pixel; seeds `1, 7, 21`. |
| Official test | 1,004 image/mask pairs | Never used for training, early stopping, hyperparameter selection or adapter debugging. |

All images are resized to 256x256 only inside the data pipeline. Train-only
augmentation is `RandomRotate90` plus horizontal flip, matching the author
trainer's stated augmentations. Test and validation receive resize and
normalization only.

## Arms and attribution

| Arm | Architecture / loss | Permitted comparison |
| --- | --- | --- |
| A: Backbone | Official `Rolling_Unet_S`; BCE+Dice loss | Whole-method reference only. |
| B: Isotropic GB | Pinned AD-GBC architecture with its existing `GranularBall(use_diag_cov=False)` scalar-scale mode; BCE+Dice plus the shared diversity regularizer. The scale-consistency term is structurally inapplicable and evaluates to zero. | Matched scalar-scale geometry-capacity control. |
| C: AD-GBC | Pinned AD-GBC architecture with `use_diag_cov=True`; BCE+Dice+author geometry loss | Existing published method transfer arm. |

The **primary attribution** is C versus B. It tests the published anisotropic
module **together with its applicable scale-consistency regularizer** against the
same-location scalar-scale mode and shared diversity regularizer. It is not a
pure “anisotropy alone” contrast because the scale-consistency term is
structurally zero in B. C versus A is secondary and tests the transfer of the
full published method; it is not evidence that anisotropy alone explains the
difference because the geometry regularizer is absent from A.

## Training budget

- Seed set: `1, 7, 21`; nine runs total.
- Batch size: 4, reducing to 2 only after an observed CUDA OOM; any reduction
  applies to every arm and seed and is recorded before a restart.
- Epoch cap: 80; Adam `1e-4`, weight decay `1e-4`, constant learning rate.
- Early stopping: patience 15 validation epochs on foreground Dice.
- Granular parameters: 32 balls, `tau=1.0`, GBC learning rate `1e-2`, diversity
  weight `0.01`, scale-consistency weight `0.1`.
- Hardware budget: RTX 4060 8GB, one GPU, 3-hour cap per run. A `RESOURCE_STOP`
  is retained, never hidden by a replacement configuration.

The runner records package versions, source commits, data SHA-256, split IDs,
per-epoch validation metrics, peak GPU memory, wall time, checkpoints and test
predictions. No test result changes the protocol.

## Metrics and gates

Primary: per-image foreground Dice on the official test split. Secondary:
foreground IoU, pixel AUPRC, Brier score, ECE, wall time and peak VRAM.

The transfer signal is reported only if all hold:

1. C exceeds B by at least 1 mean Dice point in each completed seed and the
   three-seed mean difference is at least 1 Dice point.
2. C exceeds A by at least 2 mean Dice points across seeds.
3. C does not reduce pixel AUPRC or worsen Brier score by more than 1 point
   relative to A.
4. C's median wall time and peak VRAM are no more than 1.5x A.
5. No arm has `RESOURCE_STOP`; otherwise the resource comparison is inconclusive.

Failing any condition is `KILL_ADGBC_KSDD2_TRANSFER`. A pass supports only the
bounded statement that the published AD-GBC module transferred under this exact
KSDD2 protocol.

## Pre-run adapter gate

Before the nine runs, the external runner must pass one-batch forward/backward
smokes for all three arms on a fixed 10-image subset, verify that the three
models produce 256x256 logits, and demonstrate that the only B/C constructor
difference is `use_diag_cov`. The adapter source and smoke receipts must be
reviewed before full training starts.
