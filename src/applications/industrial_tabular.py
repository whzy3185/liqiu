"""Official-source industrial tabular datasets for the first application screen."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo


@dataclass(frozen=True)
class TabularSplit:
    dataset: str
    X_train: pd.DataFrame
    y_train: np.ndarray
    X_validation: pd.DataFrame
    y_validation: np.ndarray
    X_test: pd.DataFrame
    y_test: np.ndarray
    split_protocol: str
    source: str


def load_industrial_split(name: str, seed: int, cache_dir: Path) -> TabularSplit:
    if name == "steel_plates":
        return _steel_plates(seed)
    if name == "secom":
        return _secom()
    if name == "aps_failure":
        return _aps_failure(seed, cache_dir)
    raise KeyError(f"unknown industrial dataset: {name}")


def _steel_plates(seed: int) -> TabularSplit:
    dataset = fetch_ucirepo(id=198)
    X = dataset.data.features.apply(pd.to_numeric, errors="coerce")
    target_frame = dataset.data.targets.astype(int)
    if not np.all(target_frame.sum(axis=1).to_numpy() == 1):
        raise ValueError("Steel Plates target rows are not one-hot")
    y = np.argmax(target_frame.to_numpy(), axis=1)
    train_index, test_index = train_test_split(
        np.arange(len(y)), test_size=0.2, stratify=y, random_state=seed
    )
    train_index, validation_index = train_test_split(
        train_index, test_size=0.25, stratify=y[train_index], random_state=seed
    )
    return TabularSplit(
        dataset="steel_plates",
        X_train=X.iloc[train_index].reset_index(drop=True),
        y_train=y[train_index],
        X_validation=X.iloc[validation_index].reset_index(drop=True),
        y_validation=y[validation_index],
        X_test=X.iloc[test_index].reset_index(drop=True),
        y_test=y[test_index],
        split_protocol="seeded stratified 60/20/20; no acquisition/session IDs are published",
        source="UCI 198 / DOI 10.24432/C5JG6Z",
    )


def _secom() -> TabularSplit:
    original = fetch_ucirepo(id=179).data.original.copy()
    original["timestamp"] = pd.to_datetime(
        original["timestamp"], format="mixed", dayfirst=True, errors="raise"
    )
    original = original.sort_values("timestamp").reset_index(drop=True)
    feature_columns = [column for column in original.columns if column.startswith("Attribute")]
    X = original[feature_columns].apply(pd.to_numeric, errors="coerce")
    y = (original["class"].to_numpy() == 1).astype(int)
    first = int(len(original) * 0.6)
    second = int(len(original) * 0.8)
    return TabularSplit(
        dataset="secom",
        X_train=X.iloc[:first].reset_index(drop=True),
        y_train=y[:first],
        X_validation=X.iloc[first:second].reset_index(drop=True),
        y_validation=y[first:second],
        X_test=X.iloc[second:].reset_index(drop=True),
        y_test=y[second:],
        split_protocol="chronological 60/20/20 by official production test timestamp",
        source="UCI 179 / DOI 10.24432/C54305",
    )


def _aps_failure(seed: int, cache_dir: Path) -> TabularSplit:
    dataset = fetch_openml(
        name="APSFailure",
        version=1,
        as_frame=True,
        parser="auto",
        data_home=str(cache_dir),
    )
    frame = dataset.frame.copy()
    y = (frame.pop("class").astype(str).to_numpy() == "pos").astype(int)
    X = frame.apply(pd.to_numeric, errors="coerce")
    official_train = np.arange(60_000)
    official_test = np.arange(60_000, len(frame))
    train_index, validation_index = train_test_split(
        official_train,
        test_size=0.2,
        stratify=y[official_train],
        random_state=seed,
    )
    return TabularSplit(
        dataset="aps_failure",
        X_train=X.iloc[train_index].reset_index(drop=True),
        y_train=y[train_index],
        X_validation=X.iloc[validation_index].reset_index(drop=True),
        y_validation=y[validation_index],
        X_test=X.iloc[official_test].reset_index(drop=True),
        y_test=y[official_test],
        split_protocol="official first-60000 train / last-16000 test; seeded stratified 80/20 validation inside official train",
        source="OpenML 41138 mirror of UCI 421 Scania APS Failure",
    )
