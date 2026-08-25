# Finance Dataset Inventory

## Outcome

The registry contains **12 entries representing 11 independent source families**.
South German Credit and Statlog German Credit describe the same underlying
credit sample; the former corrects coding errors and is the preferred version.
They cannot count as two independent datasets in a paper gate.

Machine-readable metadata are in `data/finance/registry.csv`.

## Task boundaries

The pool deliberately separates:

- credit/default risk: Taiwan Default, South German, Give Me Some Credit, Home
  Credit, HELOC, Lending Club;
- corporate bankruptcy: Polish Companies;
- transaction fraud: ULB/Worldline and IEEE-CIS;
- credit approval: Australian Credit;
- marketing response: Bank Marketing, retained only as a mixed tabular
  diagnostic task and never described as default/fraud prediction.

## Recommended first-round tasks

### Core low-friction tasks

| Dataset | Primary metric | Why retain |
|---|---|---|
| Taiwan Default | PR-AUC, ROC-AUC, MCC | 30k real clients, moderate imbalance, stable UCI/CC BY source |
| South German Credit | Macro-F1, MCC, bad-credit recall | corrected source with mixed numeric/categorical variables and asymmetric cost |
| HELOC | PR-AUC, MCC | real homeowner credit applications; strong tree baseline; special missing codes test local structure |
| Polish Bankruptcy | PR-AUC, MCC | five related horizons, severe imbalance and missing financial ratios |
| ULB/Worldline fraud | PR-AUC, fraud recall | extreme real fraud imbalance and explicit transaction order |

These five families are enough for an initial finance screen. Australian Credit
is a small-sample auxiliary task, not a headline dataset.

### Larger manual-download tasks

- Give Me Some Credit: 150k labeled training rows, 6.7% positives.
- Home Credit Default Risk: 307,511 application rows plus relational auxiliary
  tables; strong LightGBM/XGBoost baselines make it expensive but valuable.
- IEEE-CIS Fraud: 590,540 labeled transactions, high-dimensional sparse mixed
  features, and `TransactionDT` for chronological evaluation.
- Lending Club curated granting data: valuable time span, but provenance,
  maturity cutoff, and post-origination leakage require a dedicated audit.

## Time and target leakage rules

### ULB fraud

Use `Time` to create past-to-future train/validation/test blocks. Random
stratification mixes future transactions into training and ignores operational
drift. Any under/oversampling happens after the temporal split.

### IEEE-CIS

Use `TransactionDT` order. `TransactionID` is a join key, not a meaningful
continuous feature. All frequency/target encodings must be fit on the historical
training block only.

### Lending Club

Use issue/origination date and only application-time attributes. Exclude loan
status derivatives, payments, recoveries, collection outcomes, last-payment
fields, and every variable populated after the granting decision. Define a
maturity cutoff so recent unresolved loans are not mislabeled.

### Bank Marketing

The full release is ordered by date. `duration` is known only after a call and
must be removed if the claim is pre-call targeting. This is a response task, not
credit risk.

### Polish Bankruptcy

The five files represent different forecasting horizons and overlapping source
periods. Report horizons separately; do not present them as five independent
companies/datasets.

## Missing-value and categorical handling

- HELOC values `-7/-8/-9` are semantic missing/no-trade states, not ordered
  credit measurements.
- Home Credit and IEEE-CIS have high, structured missingness. Missing indicators
  and categorical encoders are fit inside training folds.
- Give Me Some Credit has missing `MonthlyIncome` and `NumberOfDependents`.
- Polish financial ratios contain feature-dependent missingness.
- CatBoost may consume categories directly; XGBoost/LightGBM/RF pipelines must
  receive an equivalent leakage-safe encoding budget.

## Dataset independence

The following pairs/groups are not independent evidence:

- South German and Statlog German;
- the five Polish forecasting-horizon files;
- Home Credit application and its auxiliary tables;
- alternate Kaggle/OpenML mirrors of ULB fraud.

## Exclusions and conditions

- Unattributed Kaggle reposts are excluded.
- The commonly mirrored Lending Club archive is not accepted as canonical. The
  Zenodo granting-model deposit is retained conditionally because it documents
  application-time feature selection; its file license and row roster must be
  verified before use.
- Synthetic fraud datasets such as PaySim are not needed for the first round and
  cannot count toward independent real-source paper gates.

## Prompt-3 decision

`GO`: finance has enough public tasks and the clearest 2024--2026 GB literature
space. It remains the backup because there is little direct evidence that GB
features improve already-strong boosting models.

