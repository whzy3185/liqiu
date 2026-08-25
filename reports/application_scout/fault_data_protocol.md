# Industrial Fault Data Protocol

## Pipeline

```text
raw acquisition record
-> assign physical group/unit/condition
-> train/validation/test split
-> segment independently inside each split
-> time/frequency/envelope features
-> train-only scaler and optional PCA
-> conventional ML model
```

Implementation:

- `src/applications/fault/datasets.py`
- `src/applications/fault/features.py`
- `src/applications/fault/splits.py`
- `src/applications/fault/pipeline.py`

## Indivisible leakage unit

Every raw acquisition receives a `group_id`. Prefer, in order:

1. physical bearing/machine/unit ID;
2. complete run/session ID;
3. original acquisition file ID.

All overlapping or non-overlapping windows derived from the same group stay in
one split. The code segments only after a `RecordSplit` has passed a disjoint
group assertion.

## Feature schema

The default produces 35 features per selected channel:

- 15 time-domain features;
- dominant frequency, spectral centroid/spread/RMS/entropy;
- four normalized band energies;
- top-three spectral peak frequency/energy pairs;
- high/low frequency energy ratio;
- four Hilbert-envelope features.

One to three channels yield 35--105 dimensions. Selecting enough channels to
exceed 120 dimensions raises an error. Wavelet-packet energies are optional and
require PyWavelets; they are disabled in the first round.

`clearance_factor` and `margin_factor` are retained as synonymous bearing
diagnostic names and use the same conventional peak-to-square-root-amplitude
definition. Their redundancy will be visible to tree feature importance and may
be removed after the raw baseline, not by inspecting test results.

## Split protocols

### Standard grouped split

Use recording or unit groups. Report dataset, seed, group counts, class counts,
window size, step and selected channels.

### Cross-condition

Train/validation use only source conditions. Test contains complete target
conditions. Target labels are used for scoring only.

### Chronological/run-to-failure

Sort complete groups by timestamp. Never place early and late snapshots from
the same bearing life in different splits. XJTU-SY, IMS and FEMTO require
bearing-wise protocols even when timestamps are available.

## Preprocessing

StandardScaler and PCA are fitted on extracted training windows only. Validation
and test data are transformed with the frozen training objects. Dataset adapters
must not normalize a full signal collection before record splitting.

## Signal-noise experiments

Measurement noise is injected into raw records after split assignment and before
feature extraction. Test corruption level is predefined; it cannot be selected
from test performance. Feature-space Gaussian noise is not a substitute.

## Required run metadata

- official dataset source and local checksum;
- physical group and condition keys;
- raw record roster per split;
- segment length, step and overlap;
- sampling rate and channel mapping;
- feature schema hash;
- scaler/PCA fit roster;
- seed and model configuration.

## Prompt-5 verification

`tests/test_fault_pipeline.py` checks the 35-feature schema, finite outputs,
overlapping-window group isolation, training-only scaler fit, and cross-condition
separation.

