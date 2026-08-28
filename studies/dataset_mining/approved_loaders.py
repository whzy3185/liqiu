"""Load official UCI approved candidates using their labeled train/validation portions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import arff
from sklearn.preprocessing import LabelEncoder


def load_approved_grouped(root: Path, source_dataset_id: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Load candidates whose official metadata requires a group-aware protocol.

    MicroMass has multiple spectra from the same bacterial strain.  Its mixture
    panel is deliberately excluded: the frozen extension protocol permits only
    the 571-row pure-reference, species-classification panel.
    """
    if source_dataset_id != "uci-253":
        raise ValueError(f"No grouped approved loader for {source_dataset_id}")
    data_root = root / "micromass" / "data" / "micromass"
    matrix = np.loadtxt(data_root / "pure_spectra_matrix.csv", delimiter=";")
    metadata = np.genfromtxt(
        data_root / "pure_spectra_metadata_with-species-name.csv",
        delimiter=";",
        dtype=str,
        skip_header=1,
    )
    if matrix.shape != (571, 1300) or metadata.shape != (571, 2):
        raise ValueError(f"Unexpected MicroMass pure-panel shape: matrix={matrix.shape}, metadata={metadata.shape}")
    labels = metadata[:, 0]
    groups = metadata[:, 1]
    y = LabelEncoder().fit_transform(labels)
    return matrix, y, groups, "official UCI pure-reference spectra only; species target with bacterial-strain groups; mixture spectra excluded"


def load_approved(root: Path, source_dataset_id: str) -> tuple[np.ndarray, np.ndarray, str]:
    if source_dataset_id == "uci-253":
        x, y, _groups, note = load_approved_grouped(root, source_dataset_id)
        return x, y, note
    if source_dataset_id in {"uci-372", "uci-602"}:
        if source_dataset_id == "uci-372":
            data = np.loadtxt(root / "htru2" / "HTRU_2.csv", delimiter=",")
            return data[:, :-1], data[:, -1].astype(int), "official UCI static HTRU_2.csv"
        data, _ = arff.loadarff(root / "dry_bean" / "DryBeanDataset" / "Dry_Bean_Dataset.arff")
        names = data.dtype.names
        x = np.column_stack([np.asarray(data[name], dtype=float) for name in names[:-1]])
        labels = np.asarray(data[names[-1]]).astype(str)
        return x, LabelEncoder().fit_transform(labels), "official UCI static Dry_Bean_Dataset.arff"
    if source_dataset_id == "uci-171":
        archive_root = root / "madelon"
        folder = archive_root / "MADELON"
        x = np.vstack([np.loadtxt(folder / "madelon_train.data"), np.loadtxt(folder / "madelon_valid.data")])
        y = np.concatenate([np.loadtxt(folder / "madelon_train.labels", dtype=int), np.loadtxt(archive_root / "madelon_valid.labels", dtype=int)])
        return x, y, "official UCI labeled train+validation portions; official test labels are unavailable"
    if source_dataset_id == "uci-167":
        archive_root = root / "arcene"
        folder = archive_root / "ARCENE"
        x = np.vstack([np.loadtxt(folder / "arcene_train.data"), np.loadtxt(folder / "arcene_valid.data")])
        y = np.concatenate([np.loadtxt(folder / "arcene_train.labels", dtype=int), np.loadtxt(archive_root / "arcene_valid.labels", dtype=int)])
        return x, y, "official UCI labeled train+validation portions; official test labels are unavailable"
    raise ValueError(f"No approved loader for {source_dataset_id}")
