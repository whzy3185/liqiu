"""Leakage-audited UNSW-NB15 diagnostic screen."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class IntrusionSplit:
    X_train: pd.DataFrame
    y_train: np.ndarray
    X_validation: pd.DataFrame
    y_validation: np.ndarray
    X_test: pd.DataFrame
    y_test: np.ndarray
    protocol: str


def load_unsw_nb15_screen(seed: int, cache_dir: str) -> IntrusionSplit:
    dataset = fetch_openml(data_id=46301, as_frame=True, parser="auto", data_home=cache_dir)
    frame = dataset.frame.copy()
    y = frame.pop("label").astype(int).to_numpy()
    # `attack_cat` distinguishes normal from attack types and is a direct target
    # proxy for binary detection; id/Unnamed are export row identifiers.
    X = frame.drop(columns=["id", "Unnamed: 0", "attack_cat"], errors="ignore")
    indices = np.arange(len(y))
    train, test = train_test_split(indices, test_size=0.2, stratify=y, random_state=seed)
    train, validation = train_test_split(train, test_size=0.25, stratify=y[train], random_state=seed)
    return IntrusionSplit(
        X_train=X.iloc[train].reset_index(drop=True),
        y_train=y[train],
        X_validation=X.iloc[validation].reset_index(drop=True),
        y_validation=y[validation],
        X_test=X.iloc[test].reset_index(drop=True),
        y_test=y[test],
        protocol=(
            "diagnostic seeded stratified 60/20/20 on OpenML UNSW_NB15 46301; "
            "source/destination IP, ports, timestamps, campaign files, and official raw split are unavailable "
            "in this transformed mirror, so this is not a leakage-safe primary IIoT result"
        ),
    )

