"""Application metrics with imbalance-aware industrial summaries."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
)


def industrial_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred lengths differ")
    labels = np.unique(np.concatenate([y_true, y_pred]))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    recalls = np.divide(
        np.diag(matrix),
        matrix.sum(axis=1),
        out=np.zeros(len(labels), dtype=float),
        where=matrix.sum(axis=1) > 0,
    )
    class_counts = np.asarray([(y_true == label).sum() for label in labels])
    minority = int(np.argmin(class_counts))
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "minority_recall": float(recalls[minority]),
        "g_mean": float(np.prod(np.maximum(recalls, 1e-12)) ** (1.0 / len(recalls))),
    }
