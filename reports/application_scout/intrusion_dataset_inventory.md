# IIoT / Intrusion Dataset Inventory

## Outcome

The quick registry contains nine datasets, including all seven requested
benchmarks plus X-IIoTID and WUSTL-IIOT-2021, which are directly relevant to the
2026 GBIFS paper.

Machine-readable metadata are in `data/intrusion/registry.csv`.

This direction has abundant public data but the highest leakage risk. A random
row split is not accepted as primary evidence for any dataset in the registry.

## First-round roles

| Dataset | Role | Status |
|---|---|---|
| UNSW-NB15 | manageable general network baseline with official split | retain |
| TON_IoT | heterogeneous network/telemetry IIoT screen | retain selected sources |
| X-IIoTID | direct comparator to GBIFS and balanced binary scale | retain |
| WUSTL-IIOT-2021 | smaller direct comparator with official leakage warning | retain |
| Edge-IIoTset | broad IoT/IIoT testbed | conditional after provenance audit |
| CICIDS2017 | day/scenario generalization | conditional large benchmark |
| CICIoT2023 | large real-device topology | conditional high-cost benchmark |
| BoT-IoT | extreme attack dominance and file-label coupling | conditional/high risk |
| NSL-KDD | historical compatibility only | never headline evidence |

The first Cheap Test should use no more than four: UNSW-NB15, one TON_IoT
source, X-IIoTID, and WUSTL-IIOT-2021. Larger CIC/Edge data advance only if a GB
mechanism already shows a meaningful signal.

## Leakage audit

### Direct identifiers

Remove or separately ablate:

- source/destination IP and IP-ID fields;
- Flow ID, Zeek UID, record IDs and capture-row IDs;
- exact timestamps or start/end times;
- file names and scenario labels;
- payload, URI and raw application contents when they encode the attack script;
- all label levels accidentally retained as predictive columns.

Ports and services are not automatically removed because they can be legitimate
operational signals. They require a port/service ablation: if performance
collapses when ports are removed, the model may be identifying the testbed
script rather than attack behavior.

### Dataset-specific facts

- WUSTL explicitly instructs users to remove `StartTime`, `LastTime`, `SrcAddr`,
  `DstAddr`, `sIpId`, and `dIpId` because they expose attack type.
- The Edge-IIoTset paper drops IP, ports, timestamps, payload, URI and related
  raw fields before its selected ML table. Independent checks must still inspect
  serialization/capture order.
- TON_IoT ground truth was created from attacker IP and timestamp ranges. These
  same fields cannot remain in the model.
- CICIDS2017 documents fixed attackers, victims, days, ports and attack times.
  Random rows reproduce the same campaign in train and test.
- BoT-IoT files are separated by attack category and the common 5% subset is
  almost entirely attack traffic. Sampling before scenario splitting is invalid.
- X-IIoTID contains three label levels. Every label column must be excluded, and
  alert/log-derived predictors require a target-proxy audit.

## Required split hierarchy

Use the strongest available grouping, in this order:

1. held-out capture/attack campaign;
2. held-out device or attacker/victim pair;
3. chronological past-to-future blocks;
4. official train/test split only when campaign metadata cannot be reconstructed.

Random stratified rows are permitted only as a diagnostic showing how much the
score is inflated by shared campaigns.

## Metrics

Primary metrics are Macro-F1, MCC, PR-AUC, and minority/rare-attack recall.
Accuracy is not a headline metric. Binary and multiclass results remain separate.
Thresholds are selected on validation campaigns, never on the test positive rate.

## Collision consequence

The 2026 IEEE TFUZZ GBIFS paper already evaluates X-IIoTID, TON_IoT,
WUSTL-IIOT, KDDCUP99, NSL-KDD, and UNSW-NB15. Therefore this project cannot
claim novelty from applying granular balls to IIoT intrusion. It must beat
strong boosted-tree baselines under stricter leakage-safe splits with an average
gain of at least 3 percentage points or rare-attack recall gain of at least 5
points.

## Prompt-4 decision

`HOLD`: retain IIoT as a rapid, high-bar screen. Do not invest in the largest
downloads until industrial and finance Cheap Tests establish whether the simple
GB feature/weight mechanism has a real signal.

