# AD-GBC CUDA reproduction preflight

Branch: `oush`  
Date: 2026-08-31  
Status: **CUDA smoke pass; full comparative transfer not yet frozen**

## Authority change

The earlier AD-GBC transfer audit closed the candidate because the local host
had only MPS while the pinned author trainer was CUDA-only. The user subsequently
authorized access to a Windows CUDA host. This document supersedes only that
execution blocker; it does not convert the prior one-dataset transfer into a
new method claim.

## Pinned sources and environment

| Item | Frozen value |
| --- | --- |
| Author repository | `SiaShen-dot/AD-GBC` |
| Author commit | `25abdcae0947c893320a344eda20b9606abbc79e` |
| Code license | MIT |
| Remote host | Windows via Tailscale SSH |
| GPU | NVIDIA GeForce RTX 4060, 8,188 MiB VRAM |
| Driver / CUDA UMD | NVIDIA-SMI 610.62 / CUDA 13.3 |
| Reproduction environment | `E:\\anaconda\\envs\\liqiu-adgbc`, Python 3.11 |
| PyTorch | `2.5.1+cu121`; `torch.cuda.is_available() = True` |

## Dependency reconciliation

The pinned author `requirements.txt` does not include `MedPy`, although
`metrics.py` imports it. It also pins direct packages but leaves transitive
versions unresolved. On 2026-08-31, the resolver selected `stringzilla 5.1.2`,
which lacked a usable Python-3.11 Windows wheel and failed during MSVC source
compilation. The environment therefore adds the following reproducibility
receipts without changing author source:

- `MedPy==0.5.2` and its `SimpleITK==2.5.6` dependency;
- `stringzilla==3.12.6`, a downloaded `cp311-win_amd64` wheel satisfying
  `albucore==0.0.21`'s lower bound;
- the remaining requirements' transitive dependencies installed as wheels.

`pip check` reports **No broken requirements found** after this reconciliation.
This is an environment-compatibility patch, not a model modification.

## KSDD2 acquisition and integrity

| Check | Result |
| --- | --- |
| Source | Official ViCoS KSDD2 ZIP, downloaded by Windows BITS task `KSDD2-Official` |
| Archive size | 853,126,555 bytes |
| Local SHA-256 | `edcdb486809b24f1d17b785e30c52fafc5999554dd5fe18ddf77b61ceb6f36a8` |
| Archive listing | Read successfully; contains `train/`, `test/`, images and `_GT.png` masks |
| Train split | 2,331 paired non-copy image/mask records |
| Test split | 1,004 paired image/mask records |
| Duplicate handling | `10301 (copy).png` and `10301_GT (copy).png` are duplicate archive entries; excluded by explicit filename rule, not assigned synthetic labels |
| License | CC BY-NC-SA 4.0 per official KSDD2 page |

## CUDA smoke

Ten deterministic hard-linked samples (`10000` through `10009`) from the
official train split were exposed to the unchanged author trainer through a
separate `inputs/ksdd2_smoke` data directory. No original image, mask or author
source file was changed.

Command contract:

```text
train_GBC.py --dataset ksdd2_smoke --name ksdd2_smoke_adgbc
--arch GBC_Rolling_Unet_S --epochs 1 --batch_size 1 --num_workers 0
--input_w 256 --input_h 256 --scheduler ConstantLR
--div_weight 0.01 --scale_weight 0.1
```

Result: **PASS**. The run completed 8 training batches and 2 validation batches,
produced `model.pth` (7,359,138 bytes), `config.yml` and `log.csv`, and emitted
no CUDA OOM or data-format exception. The observed post-run GPU state was
approximately 1,540 MiB / 8,188 MiB. The smoke's validation IoU/Dice of 1.0 is
not an efficacy result: the set is only ten images and the trainer creates a
random internal split.

The official no-AD-GBC comparator was then located in the AD-GBC repository's
explicit Rolling-Unet acknowledgement: `Jiaoyang45/Rolling-Unet`, commit
`8a43d40c218917e454c0584a853757e3a2cf9c80`, MIT.  Its architecture has the
same S/M/L capacity family without the two GBC calls.  The original baseline
trainer had one compatibility issue: it calls the removed Albumentations
`transforms.Flip` symbol.  An external launcher aliases that symbol to the
semantically identical `HorizontalFlip` at runtime; author source remains
byte-for-byte unchanged.  The same 10-pair one-epoch CUDA smoke completed for
the baseline as well.

Finally, a separate official-split external runner completed one-epoch
forward/backward/evaluation smokes for all three frozen arms.  The observed peak
CUDA allocations were approximately 140 MB (Backbone), 384 MB (isotropic GB)
and 384 MB (AD-GBC).  Its first smoke subset was all background, so its apparent
Dice=1/AUPRC=0 measurements are explicitly non-efficacy diagnostics; the runner
was corrected before formal runs to include five foreground and five background
records in each smoke subset.

## Remaining full-experiment gate

The unchanged author trainer randomly holds out 20% from a single input folder;
it cannot consume KSDD2's official train/test split directly. A full transfer
study must therefore use an external data-directory/runner adapter while keeping
the AD-GBC module byte-identical, record the author-style internal validation
split, and evaluate only once on the official 1,004-image test split.

Before any full training, audit whether the repository contains genuinely
matched no-AD-GBC and isotropic-region architecture controls. If it does not,
the candidate remains a bounded CUDA transfer reproduction, not a valid causal
test of anisotropic granular-ball geometry.
