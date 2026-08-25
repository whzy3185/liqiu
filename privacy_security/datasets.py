from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml, load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class PrivacyDataset:
    name: str
    X: np.ndarray
    y: np.ndarray
    sensitive: np.ndarray
    sensitive_index: int
    sensitive_name: str
    provenance: str


OPENML_SPECS = {
    "adult": (1590, "sex"),
    # OpenML 1461 anonymizes the original columns; V3 is marital status.
    "bank_marketing": (1461, "V3"),
    "german_credit": (31, "personal_status"),
    "covertype": (1596, "Elevation"),
}


def load_dataset(name: str, *, seed: int, cap: int, data_home: Path) -> PrivacyDataset:
    if name == "breast_cancer":
        bunch = load_breast_cancer(as_frame=True)
        frame = bunch.data.copy()
        target = pd.Series(bunch.target, index=frame.index)
        sensitive_name = "mean radius"
        provenance = "sklearn.datasets.load_breast_cancer"
    else:
        data_id, sensitive_name = OPENML_SPECS[name]
        bunch = fetch_openml(data_id=data_id, as_frame=True, data_home=str(data_home), parser="auto")
        frame = bunch.data.copy()
        target = pd.Series(bunch.target, index=frame.index)
        provenance = f"OpenML data_id={data_id}, version={getattr(bunch, 'version', 'unknown')}"

    frame = frame.replace([np.inf, -np.inf], np.nan)
    valid = target.notna() & frame.notna().all(axis=1)
    frame, target = frame.loc[valid].reset_index(drop=True), target.loc[valid].reset_index(drop=True)
    sensitive_raw = frame.pop(sensitive_name)
    sensitive = _binary_sensitive(sensitive_raw)
    y = LabelEncoder().fit_transform(target.astype(str))

    if len(frame) > cap:
        indices = np.arange(len(frame))
        strata = np.char.add(y.astype(str), sensitive.astype(str))
        try:
            kept, _ = train_test_split(indices, train_size=cap, stratify=strata, random_state=seed)
        except ValueError:
            kept, _ = train_test_split(indices, train_size=cap, stratify=y, random_state=seed)
        frame, y, sensitive = frame.iloc[kept].reset_index(drop=True), y[kept], sensitive[kept]

    categorical = list(frame.select_dtypes(exclude=[np.number, "bool"]).columns)
    numeric = [column for column in frame.columns if column not in categorical]
    transformer = ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
        ],
        sparse_threshold=0.0,
    )
    public = np.asarray(transformer.fit_transform(frame), dtype=float)
    private_coordinate = StandardScaler().fit_transform(sensitive.reshape(-1, 1))
    X = np.column_stack([public, private_coordinate])
    return PrivacyDataset(
        name=name,
        X=X,
        y=np.asarray(y),
        sensitive=np.asarray(sensitive),
        sensitive_index=X.shape[1] - 1,
        sensitive_name="marital" if name == "bank_marketing" else sensitive_name,
        provenance=provenance,
    )


def _binary_sensitive(series: pd.Series) -> np.ndarray:
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series)
        return (numeric > numeric.median()).astype(int).to_numpy()
    text = series.astype(str)
    counts = text.value_counts()
    if len(counts) == 2:
        return (text == counts.index[0]).astype(int).to_numpy()
    # A deterministic one-vs-rest target avoids choosing the easiest category.
    reference = sorted(counts.index.astype(str))[0]
    return (text == reference).astype(int).to_numpy()
