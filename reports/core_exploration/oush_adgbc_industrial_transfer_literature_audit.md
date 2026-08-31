# Phase 2 — Audit: AD-GBC industrial dense-prediction transfer

Branch: `oush`  
Date audited: 2026-08-31  
Phase-1 artifact: `oush_adgbc_industrial_transfer_phase1.md`  
Status: **KILL — unchanged author code is CUDA-only on the available MPS host**

## Audit outcome

The candidate passes identity, software-license and target-data-license screening but fails the
pre-frozen executable-code gate. The official AD-GBC source is explicitly a
CVPR-2026 medical-segmentation implementation, carries an MIT license, includes
training/evaluation entry points, and accepts a generic binary image/mask folder
layout. However, the pinned source (`25abdcae0947c893320a344eda20b9606abbc79e`)
hard-codes CUDA placement throughout `train_GBC.py`:

- input and target batches call `.cuda()`;
- losses call `.cuda()`;
- model creation calls `model.cuda()`;
- seeding and cache cleanup call `torch.cuda.*`.

The only attached accelerator is Apple M5 Metal/MPS; no CUDA device is present.
The source's pinned requirements include `torch==2.5.1` and `torchvision==0.20.1`
but no MPS/device abstraction. Therefore the unchanged official training path
cannot satisfy the Phase-1 MPS smoke gate. Replacing `.cuda()` calls, adding a
device abstraction, or modifying the trainer would be a ported implementation,
not the frozen unchanged-author-code transfer.

## Source and data verification

| Gate | Evidence | Verdict |
| --- | --- | --- |
| Author method identity | Official repository calls itself the implementation of *AD-GBC: Anisotropic Granular-Ball Skip-Connection Refiner for UNet-Based Medical Image Segmentation*, accepted at CVPR 2026. | PASS |
| Software license | Pinned repository `LICENSE` is MIT. | PASS |
| Runnable segmentation surface | Repository includes `train_GBC.py`, `val_GBC.py`, dataset loader, architecture and requirements files. | PASS for CUDA only |
| Current accelerator compatibility | Pinned trainer hard-codes CUDA; local hardware exposes MPS/Metal only. | **FAIL** |
| Target task type | Official KSDD2 page documents annotated surface-defect images; the locally inspectable mask schema was not verified because the CUDA gate already fails before dataset download. | UNRESOLVED |
| Target dataset license | KSDD2 is CC BY-NC-SA 4.0; research/non-commercial use is compatible with a non-commercial study subject to attribution/share-alike obligations. | PASS |
| Target size and split | Official KSDD2 counts: 3,335 images, 356 defective, 2,979 non-defective; train 246/2,085 and test 110/894 positive/negative. | PASS |
| Direct prior industrial AD-GBC transfer | No accepted/published AD-GBC-to-KSDD2 transfer was located in the bounded exact-name search. SegGBC nevertheless already occupies clustering-based image segmentation. | UNKNOWN / adjacent collision |

The [official AD-GBC repository](https://github.com/SiaShen-dot/AD-GBC) documents
the module, binary-mask folder structure and CUDA-oriented training commands.
The [official KSDD2 page](https://www.vicos.si/resources/kolektorsdd2/) documents
the annotated-defect dataset, fixed split and CC BY-NC-SA 4.0 license. The published
[SegGBC CVPR 2026 paper](https://openaccess.thecvf.com/content/CVPR2026/html/Chong_SegGBC_Justifiable_Coarse-to-Fine_Granular-Ball_Computing_for_Enhancing_Clustering_Image_Segmentation_CVPR_2026_paper.html)
is an additional collision risk for a general GB image-segmentation claim.

## Mechanism and novelty decision

AD-GBC is already a learnable anisotropic granular-region module with explicit
geometry regularizers and medical segmentation evaluations. A KSDD2 result could
at most be a bounded cross-domain replication; it cannot be described as a new
GB module or a general industrial segmentation method. More importantly, the
frozen experiment requires the unchanged author module to run on this MPS host.
That condition fails before data download, adapter construction or metric
selection.

```text
Author-code identity/license: PASS
KSDD2 license/split: PASS; local mask-schema check: UNRESOLVED
Unchanged code on available MPS hardware: FAIL
Phase-2B download, adapter work and training: DO NOT RUN
Candidate: KILL_ADGBC_TRANSFER
```

## Reproducibility record

- Pinned source commit: `25abdcae0947c893320a344eda20b9606abbc79e`.
- Repository tree and source files were read remotely; no author source was
  copied into this repository.
- Local hardware check: Apple M5, 10-core built-in GPU, Metal support; no CUDA
  device reported.
- No KSDD2 file was downloaded, no environment was installed, and no author or
  derived code was changed.

## References

1. Shen, X., Zhao, Q., & Feng, L. (2026). *AD-GBC: Anisotropic granular-ball
   skip-connection refiner for UNet-based medical image segmentation*. CVPR
   2026. Official source and code: [AD-GBC](https://github.com/SiaShen-dot/AD-GBC).
2. Božič, J., Tabernik, D., & Skočaj, D. (2021). Mixed supervision for
   surface-defect detection: From weakly to fully supervised learning.
   *Computers in Industry*. Dataset: [KolektorSDD2](https://www.vicos.si/resources/kolektorsdd2/).
3. Chong, Q., Zeng, W., Shen, X., Li, J., Yin, Q., & Zheng, X. (2026).
   [SegGBC: Justifiable coarse-to-fine granular-ball computing for enhancing
   clustering image segmentation](https://openaccess.thecvf.com/content/CVPR2026/html/Chong_SegGBC_Justifiable_Coarse-to-Fine_Granular-Ball_Computing_for_Enhancing_Clustering_Image_Segmentation_CVPR_2026_paper.html).
   *CVPR 2026*, 42104–42114.
