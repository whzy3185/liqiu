# Adaptive Purity Validity Literature Collision Audit

| claim | GBC evidence | generic-tree collision | novelty risk | decision |
| --- | --- | --- | --- | --- |
| C1 purity is granule quality | GBS, VPGB, GBCRS and recent purity-guided GB work explicitly use purity as a stopping/quality quantity | none needed | low | retain as factual use case |
| C2 purity supports clean/noisy or local-reliability decisions | GBS/VPGB/GBCRS and recent purity-guided methods make robustness or local-quality claims | generic sample-selection confidence literature is adjacent | medium | retain only with exact downstream wording |
| C3 adaptive terminal purity is optimistic out of sample | no scoped GBC study located with independent fresh routing of frozen terminal balls | direct analogue: adaptive decision-tree leaf frequency optimism/calibration | high | test only relative to generic controls |
| C4 optimism grows with refinement | no scoped GBC depth/support-controlled fresh audit located | small-leaf and post-selection effects are established | high | require depth/support matching |
| C5 higher tau raises train purity without fresh improvement | GBC papers discuss threshold/noise performance but no scoped independent terminal-reliability curve located | calibration thresholding is adjacent | medium | primary synthetic-oracle test |
| C6 stopping adds bias beyond generic small-cell estimation | no located direct comparison | generic tree leaves are a strong positive control | very high | must include CART and X-only frontier controls |
| C7 honest/cross-fit purity corrects the gap | no located GBC systematic comparison | honest estimation, smoothing and Venn-Abers are mature | high | use only as control, never new method |
| C8 certified purity improves GBC | no basis before C3--C7 pass | selective/post-selection inference is mature | high | prohibited before evidence gate |

## Gate

Decision: `GO_PURITY_VALIDITY_CHEAP_TEST`.

The gate is narrow. Existing probability-estimation-tree work directly covers
extreme leaf frequencies and their calibration, so “purity is miscalibrated” is
not a candidate contribution.  The scoped GBC material uses empirical purity
as construction/quality/noise evidence, yet no direct collision was located
that evaluates adaptively selected terminal balls by independently routed fresh
reliability with support/depth and generic-leaf controls.  The Cheap Test must
therefore either isolate a residual GBC-specific selection pattern or kill the
line.
