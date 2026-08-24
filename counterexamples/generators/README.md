# Synthetic generator requirements

Generators must expose every stress parameter, accept an explicit seed, return
ground-truth metadata when available, and be serializable from an experiment
configuration. The initial suite targets geometry, noise, drift, imbalance, and
ambient/intrinsic dimensionality.

`synthetic.py` currently implements 12 deterministic binary families: Gaussian
blobs, moons, circles, XOR, checkerboard, spirals, thin manifold, nested
clusters, anisotropic clusters, multimodal classes, varying density, and
imbalanced density. Shared transforms add symmetric/asymmetric/boundary/
cluster-specific label noise, feature noise, outliers, and ambient-dimension
embedding.

Passing a generator test establishes only that its shape, labels, and seeds are
valid. It does not establish a model failure.
