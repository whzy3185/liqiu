"""Leakage-safe industrial fault feature pipeline."""

from .datasets import SignalRecord, SignalWindow, WindowConfig, segment_record
from .features import FeatureConfig, extract_features
from .pipeline import FaultFeatureDataset, FaultFeaturePipeline, PreprocessConfig
from .splits import RecordSplit, cross_condition_split, grouped_train_val_test

__all__ = [
    "SignalRecord",
    "SignalWindow",
    "WindowConfig",
    "segment_record",
    "FeatureConfig",
    "extract_features",
    "FaultFeatureDataset",
    "FaultFeaturePipeline",
    "PreprocessConfig",
    "RecordSplit",
    "cross_condition_split",
    "grouped_train_val_test",
]

