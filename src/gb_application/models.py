"""Model helpers for raw plus GB feature matrices."""
from __future__ import annotations

import numpy as np


def append_gb_features(X: np.ndarray, gb_features: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    gb_features = np.asarray(gb_features, dtype=float)
    if X.ndim != 2 or gb_features.ndim != 2 or len(X) != len(gb_features):
        raise ValueError("raw and GB feature matrices are incompatible")
    return np.column_stack([X, gb_features])

