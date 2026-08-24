# Baseline policy

Priority order is official author code, supplementary code, credible independent
reproduction, then a paper-faithful local implementation. Any deviation from a
paper is documented. Baselines are not weakened, and failed reproduction
attempts remain in the logs.

Planned common interface:

```python
fit(X, y)
predict(X)
predict_proba(X)
get_structure()
```

`get_structure()` should expose granules, centers, radii, members, purity,
labels, and uncertainty whenever the method defines them.

