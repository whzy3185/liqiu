# Classical baselines

KNN, SVM, random forest, AdaBoost, KMeans, and DBSCAN adapters will use the same
data split, seed, preprocessing, and metric protocol as granular methods.

`models.py` now provides the required uniform interface for all six baselines.
Clustering `predict_proba` is an adapter convenience (distance-softmax for KMeans,
one-hot cluster/noise assignment for DBSCAN), not a probabilistic claim.
