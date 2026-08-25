import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from applications.fault import (
    FaultFeaturePipeline,
    FeatureConfig,
    PreprocessConfig,
    SignalRecord,
    WindowConfig,
    cross_condition_split,
    extract_features,
    grouped_train_val_test,
)


def synthetic_records() -> list[SignalRecord]:
    records = []
    fs = 1024.0
    time = np.arange(1024) / fs
    for index in range(18):
        label = index % 2
        condition = "A" if index < 12 else "B"
        frequency = 40.0 if label == 0 else 120.0
        signal = np.sin(2 * np.pi * frequency * time) + 0.02 * index
        records.append(
            SignalRecord(
                signal=signal,
                label=label,
                group_id=f"unit-{index}",
                unit_id=f"unit-{index}",
                record_id=f"record-{index}",
                condition=condition,
                timestamp=float(index),
                sampling_rate=fs,
            )
        )
    return records


class FaultPipelineTests(unittest.TestCase):
    def test_feature_schema_is_compact_and_finite(self):
        record = synthetic_records()[0]
        values, names = extract_features(record.signal, record.sampling_rate, FeatureConfig())
        self.assertEqual(len(values), 35)
        self.assertEqual(len(names), 35)
        self.assertTrue(np.isfinite(values).all())
        self.assertIn("ch0_spectral_entropy", names)
        self.assertIn("ch0_envelope_kurtosis", names)

    def test_split_before_overlapping_windows_prevents_leakage(self):
        split = grouped_train_val_test(synthetic_records(), seed=7)
        pipeline = FaultFeaturePipeline(
            WindowConfig(size=256, step=64),
            preprocess=PreprocessConfig(standardize=True),
        )
        dataset = pipeline.fit_transform(split)
        train_groups = set(dataset.groups_train)
        validation_groups = set(dataset.groups_validation)
        test_groups = set(dataset.groups_test)
        self.assertFalse(train_groups & validation_groups)
        self.assertFalse(train_groups & test_groups)
        self.assertFalse(validation_groups & test_groups)
        self.assertGreater(len(dataset.y_train), len(split.train))
        self.assertEqual(dataset.X_train.shape[1], 35)

    def test_scaler_is_fit_on_training_features_only(self):
        split = grouped_train_val_test(synthetic_records(), seed=21)
        raw_pipeline = FaultFeaturePipeline(
            WindowConfig(size=256, step=256),
            preprocess=PreprocessConfig(standardize=False),
        )
        raw = raw_pipeline.fit_transform(split)
        scaled_pipeline = FaultFeaturePipeline(
            WindowConfig(size=256, step=256),
            preprocess=PreprocessConfig(standardize=True),
        )
        scaled = scaled_pipeline.fit_transform(split)
        np.testing.assert_allclose(scaled_pipeline.scaler_.mean_, raw.X_train.mean(axis=0))
        np.testing.assert_allclose(scaled.X_train.mean(axis=0), 0.0, atol=1e-8)

    def test_cross_condition_keeps_target_condition_out(self):
        split = cross_condition_split(
            synthetic_records(),
            train_conditions={"A"},
            test_conditions={"B"},
            seed=1,
        )
        self.assertEqual({record.condition for record in split.train}, {"A"})
        self.assertEqual({record.condition for record in split.validation}, {"A"})
        self.assertEqual({record.condition for record in split.test}, {"B"})


if __name__ == "__main__":
    unittest.main()

