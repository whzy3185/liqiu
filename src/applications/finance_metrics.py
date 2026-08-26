"""Threshold-free and validation-thresholded finance metrics."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_auc_score,
)


def choose_validation_threshold(y: np.ndarray, probability: np.ndarray) -> float:
    candidates = np.unique(np.r_[0.01, np.linspace(0.02, 0.98, 97), probability])
    scores = [matthews_corrcoef(y, probability >= threshold) for threshold in candidates]
    return float(candidates[int(np.argmax(scores))])


def finance_metrics(y_true: np.ndarray, probability: np.ndarray, threshold: float) -> dict[str, float]:
    prediction = np.asarray(probability >= threshold, dtype=int)
    y_true = np.asarray(y_true, dtype=int)
    return {
        "pr_auc": float(average_precision_score(y_true, probability)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "macro_f1": float(f1_score(y_true, prediction, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, prediction)),
        "recall_positive": float(np.mean(prediction[y_true == 1] == 1)),
        "threshold": float(threshold),
    }

