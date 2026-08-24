# Synthetic generator requirements

Generators must expose every stress parameter, accept an explicit seed, return
ground-truth metadata when available, and be serializable from an experiment
configuration. The initial suite targets geometry, noise, drift, imbalance, and
ambient/intrinsic dimensionality.

