# Industrial Fault Dataset Inventory

## Outcome

The registry contains **13 dataset entries**: 12 physical-rig/machine releases
from 11 independent physical-data programs (the two Ottawa releases share an
institution), plus the Tennessee Eastman simulated process benchmark. Tennessee
Eastman is explicitly marked non-real.

Machine-readable metadata are in `data/industrial_fault/registry.csv`.

No large archive was downloaded in this stage. Official availability, license,
physical unit structure, sensor type, operating conditions, and leakage-safe
protocol were evaluated before spending storage or compute.

## Source tiers

### Tier A: first-round classification candidates

| Dataset | Why retain | Required split |
|---|---|---|
| Paderborn | real and artificial bearing damage; named bearing units; vibration/current; multiple conditions | leave-bearing-ID-out and cross-condition |
| HUST | five bearing types, three conditions, single and compound defects, CC BY 4.0 | group by raw recording and bearing type |
| SEU | bearing and gearbox subsets, eight channels, two conditions | file-level A-to-B/B-to-A |
| UConn | 936 balanced recording-level gear samples, nine classes and severity | recording-level; optional severity holdout |
| Ottawa constant | multimodal sensors, bearing IDs and developing/faulty stages | leave-bearing-ID-out |
| CWRU | standard benchmark with loads, speeds, seeded fault sizes | original-file split and cross-load; never random windows |

These six independent sources are sufficient to start the raw conventional-ML
baseline and satisfy the minimum source breadth for a first Cheap Test.

### Tier B: useful after ingestion work

| Dataset | Use |
|---|---|
| MFPT | load robustness plus three real-machine external cases |
| Ottawa variable-speed | explicit speed-profile shift |
| PHM 2009 gearbox | cross-speed/load/gear-type and multi-label diagnosis |

### Tier C: run-to-failure/prognostics data

| Dataset | Constraint |
|---|---|
| XJTU-SY | 15 bearing lives; no universal independent window labels |
| IMS | three tests/four bearings; snapshots are temporally dependent |
| FEMTO/PRONOSTIA | accelerated bearing lives; challenge is mainly RUL/prognostics |

These data are valuable for health-stage, anomaly, or cross-unit studies, but
they must not be converted into thousands of randomly split “independent”
classification windows.

### Separate process benchmark

Tennessee Eastman contains multivariate simulated chemical-process trajectories.
It can test general process fault detection, but it is not evidence on real
vibration sensors or physical machine-to-machine generalization.

## Leakage risks by dataset family

### Long recording datasets

CWRU, HUST, SEU, MFPT, Ottawa, and PHM 2009 contain recordings from which many
windows can be extracted. The recording/session identifier is the grouping key.
Segmentation happens **after** assignment to train/validation/test.

Forbidden protocol:

```text
one long signal -> overlapping windows -> random train/test split
```

Required protocol:

```text
physical recording/unit/condition -> split -> segment independently inside split
```

### Run-to-failure datasets

XJTU-SY, IMS, and FEMTO have strong temporal dependence. Whole bearing lives
must be held out. Early-life observations cannot appear in train while later
snapshots from the same bearing appear in test.

### Condition-shift datasets

Paderborn, HUST, SEU, Ottawa variable-speed, PHM 2009, and XJTU-SY support
condition-based evaluation. Random-split results are diagnostic only; the paper
value comes from cross-condition or cross-unit generalization.

## License and access findings

- Paderborn: explicit CC BY-NC 4.0.
- HUST, both Ottawa releases, and UConn: CC BY 4.0.
- IMS: public NASA distribution with U.S. government-work metadata.
- CWRU, XJTU-SY, SEU, MFPT, PHM 2009, and FEMTO: no explicit reusable data
  license was verified. Download from the canonical source, cite it, cache
  locally, and do not redistribute raw files.

## Recommended download order

1. HUST -- citable DOI, manageable 99 recordings, clear unit/condition design.
2. UConn -- small, balanced, recording-level samples, CC BY 4.0.
3. Ottawa constant -- multimodal and bearing-ID-aware, CC BY 4.0.
4. Paderborn -- strong real/artificial damage and condition structure.
5. CWRU -- necessary literature baseline, but use only leakage-safe file splits.
6. SEU -- useful cross-condition task; requires manual canonical download and
   parser validation.
7. MFPT and Ottawa variable-speed after the first pipeline is stable.

## Prompt-2 decision

`GO`: the public industrial data pool is large enough for a multi-source paper.
The limiting factor is not data count; it is rigorous recording/unit/condition
splitting and consistent feature extraction.
