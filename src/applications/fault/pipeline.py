"""Split-first fault feature extraction and train-only preprocessing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .datasets import SignalWindow, WindowConfig, segment_record
from .features import FeatureConfig, extract_features
from .splits import RecordSplit, assert_no_group_leakage


@dataclass(frozen=True)
class PreprocessConfig:
    standardize: bool = True
    pca_components: int | float | None = None


@dataclass(frozen=True)
class FaultFeatureDataset:
    X_train: np.ndarray
    y_train: np.ndarray
    groups_train: np.ndarray
    X_validation: np.ndarray
    y_validation: np.ndarray
    groups_validation: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    groups_test: np.ndarray
    feature_names: tuple[str, ...]


class FaultFeaturePipeline:
    def __init__(
        self,
        window: WindowConfig,
        features: FeatureConfig = FeatureConfig(),
        preprocess: PreprocessConfig = PreprocessConfig(),
    ) -> None:
        self.window = window
        self.features = features
        self.preprocess = preprocess
        self.scaler_: StandardScaler | None = None
        self.pca_: PCA | None = None
        self.feature_names_: tuple[str, ...] | None = None

    def fit_transform(self, split: RecordSplit) -> FaultFeatureDataset:
        assert_no_group_leakage(split)
        train = self._extract_split(split.train)
        validation = self._extract_split(split.validation)
        test = self._extract_split(split.test)
        X_train, y_train, groups_train, names = train
        X_validation, y_validation, groups_validation, validation_names = validation
        X_test, y_test, groups_test, test_names = test
        if names != validation_names or names != test_names:
            raise RuntimeError("feature schema differs across splits")
        self.feature_names_ = tuple(names)

        if self.preprocess.standardize:
            self.scaler_ = StandardScaler().fit(X_train)
            X_train = self.scaler_.transform(X_train)
            X_validation = self.scaler_.transform(X_validation)
            X_test = self.scaler_.transform(X_test)
        if self.preprocess.pca_components is not None:
            self.pca_ = PCA(n_components=self.preprocess.pca_components).fit(X_train)
            X_train = self.pca_.transform(X_train)
            X_validation = self.pca_.transform(X_validation)
            X_test = self.pca_.transform(X_test)
            names = [f"pca_{index}" for index in range(X_train.shape[1])]
        return FaultFeatureDataset(
            X_train=X_train,
            y_train=y_train,
            groups_train=groups_train,
            X_validation=X_validation,
            y_validation=y_validation,
            groups_validation=groups_validation,
            X_test=X_test,
            y_test=y_test,
            groups_test=groups_test,
            feature_names=tuple(names),
        )

    def _extract_split(
        self, records: tuple
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
        windows: list[SignalWindow] = []
        for record in records:
            windows.extend(segment_record(record, self.window))
        if not windows:
            raise ValueError("a split produced no windows")
        rows: list[np.ndarray] = []
        names: list[str] | None = None
        for window in windows:
            values, current_names = extract_features(
                window.signal,
                window.sampling_rate,
                self.features,
            )
            if names is None:
                names = current_names
            elif names != current_names:
                raise RuntimeError("inconsistent extracted feature names")
            rows.append(values)
        return (
            np.vstack(rows),
            np.asarray([window.label for window in windows]),
            np.asarray([window.group_id for window in windows], dtype=object),
            names or [],
        )

