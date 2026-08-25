# Application scout protocol

## Objective

Find one real application where granular-ball augmentation raises a strong,
fairly tuned conventional ML baseline enough to support an application paper.

## Downstream model order

XGBoost, LightGBM, CatBoost, Random Forest, ExtraTrees, and KNN. RBF-SVM is a
necessary diagnostic baseline, not a proposed innovation.

## Non-negotiable controls

- Test data never selects datasets, features, thresholds, hyperparameters, or
  GB variants.
- The same tuning budget is assigned to raw and GB-enhanced models.
- Signals from the same continuous acquisition, physical unit, condition, or
  time period cannot leak across train and test.
- Scalers, PCA, selection, resampling, and granular structures are fit inside
  the training fold only.
- Supervised GB features for training samples are produced out of fold.
- Failed runs and negative datasets remain in the result ledger.
- Performance against the strongest conventional baseline determines
  `GO`, `HOLD`, or `KILL`.

## Round-one stop

Execute prompts 0--17, then stop algorithm development and rank applications.
Keep exactly one application, retain at most one backup, and kill the rest.

## Paper gate

The final paper gate is frozen before formal tuning:

- at least five independent real data sources;
- mean primary-metric gain at least 0.02 over the strongest tuned baseline;
- win rate at least 70%;
- at least three datasets with gain at least 0.03;
- at least one real difficult setting with gain at least 0.05;
- the gain survives equal-budget tuning and a leakage audit.

