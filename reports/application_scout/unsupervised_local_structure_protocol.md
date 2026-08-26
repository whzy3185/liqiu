# Unsupervised Local-Structure Reopen Protocol

## Why this is a distinct mechanism

The killed Prompt-8 mechanism generated balls with training labels and exposed
purity, label entropy, same-label distance, and other-label distance. This
reopen test uses **no labels at all** for representation construction and never
assigns a query sample a label-derived feature.

The resulting representation is a recursive geometric ball cover. Its features
are center distance, normalized center distance, radius, log size, density,
depth, nearest-ball separation, boundary margin, and overlap-neighbor count.

## Necessary control

For every dataset/seed, KMeans is fit with exactly the final number of
unsupervised balls. KMeans receives the same feature schema except ball depth,
which is fixed to zero. Both variants use the same training data, preprocessing,
model hyperparameters, and downstream full-data fit.

## Fixed settings

- recursive radius/size split through two-means;
- no label input;
- maximum 128 regions;
- minimum 20 samples per final region;
- APS representation fitting cap: label-free seeded uniform 12,000 training rows;
- no parameter search;
- Steel Plates, SECOM, and APS; five frozen seeds;
- XGBoost, LightGBM, CatBoost, Random Forest, ExtraTrees.

## Decision

The mechanism is `GO` only if, relative to both Raw and matched KMeans features:

1. at least two of three datasets have mean Macro-F1 gain >= +1pp; and
2. at least one dataset has gain >= +2pp; and
3. the mean UGBFeat-minus-KMeans delta is positive on at least two datasets.

If these conditions fail, do not build a third local-structure feature variant.
