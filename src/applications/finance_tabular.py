"""Official-source finance datasets for the first GB application screen."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo


@dataclass(frozen=True)
class FinanceSplit:
    dataset: str
    X_train: pd.DataFrame
    y_train: np.ndarray
    X_validation: pd.DataFrame
    y_validation: np.ndarray
    X_test: pd.DataFrame
    y_test: np.ndarray
    split_protocol: str
    source: str


def load_finance_split(name: str, seed: int) -> FinanceSplit:
    if name == "taiwan_default":
        return _taiwan_default(seed)
    if name == "australian_credit":
        return _australian_credit(seed)
    if name == "polish_bankruptcy_5year":
        return _polish_5year(seed)
    raise KeyError(f"unknown finance dataset: {name}")


def _partition(X: pd.DataFrame, y: np.ndarray, *, seed: int, dataset: str, protocol: str, source: str) -> FinanceSplit:
    indices = np.arange(len(y))
    train, test = train_test_split(indices, test_size=0.2, stratify=y, random_state=seed)
    train, validation = train_test_split(train, test_size=0.25, stratify=y[train], random_state=seed)
    return FinanceSplit(
        dataset=dataset,
        X_train=X.iloc[train].reset_index(drop=True),
        y_train=y[train],
        X_validation=X.iloc[validation].reset_index(drop=True),
        y_validation=y[validation],
        X_test=X.iloc[test].reset_index(drop=True),
        y_test=y[test],
        split_protocol=protocol,
        source=source,
    )


def _taiwan_default(seed: int) -> FinanceSplit:
    dataset = _uci_cached(350)
    X = dataset.data.features.copy().drop(columns=["ID"], errors="ignore")
    y = dataset.data.targets.iloc[:, 0].astype(int).to_numpy()
    return _partition(
        X,
        y,
        seed=seed,
        dataset="taiwan_default",
        protocol="seeded stratified 60/20/20; no reliable row-level temporal ordering in release",
        source="UCI 350 / DOI 10.24432/C55S3H",
    )


def _australian_credit(seed: int) -> FinanceSplit:
    dataset = _uci_cached(143)
    X = dataset.data.features.copy()
    y = dataset.data.targets.iloc[:, 0].astype(int).to_numpy()
    return _partition(
        X,
        y,
        seed=seed,
        dataset="australian_credit",
        protocol="seeded stratified 60/20/20; anonymized application rows have no valid event order",
        source="UCI 143 / DOI 10.24432/C59012",
    )


def _polish_5year(seed: int) -> FinanceSplit:
    original = _uci_cached(365).data.original.copy()
    subset = original[original["year"] == 5].drop(columns=["year"]).reset_index(drop=True)
    y = subset.pop("class").astype(int).to_numpy()
    return _partition(
        subset,
        y,
        seed=seed,
        dataset="polish_bankruptcy_5year",
        protocol="seeded stratified 60/20/20 within the 5-year forecasting-horizon task; horizons are not pooled",
        source="UCI 365 / DOI 10.24432/C5F600",
    )


@lru_cache(maxsize=None)
def _uci_cached(identifier: int):
    """Avoid repeated network access across seeds in one experiment process."""
    return fetch_ucirepo(id=identifier)
