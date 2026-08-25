"""Recording-, unit-, condition-, and time-aware split policies."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .datasets import SignalRecord


@dataclass(frozen=True)
class RecordSplit:
    train: tuple[SignalRecord, ...]
    validation: tuple[SignalRecord, ...]
    test: tuple[SignalRecord, ...]

    def __post_init__(self) -> None:
        if not self.train or not self.validation or not self.test:
            raise ValueError("train, validation, and test must all contain records")
        assert_no_group_leakage(self)


def grouped_train_val_test(
    records: Sequence[SignalRecord],
    *,
    seed: int,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> RecordSplit:
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("split fractions must lie in (0, 1)")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("train + validation fractions must be < 1")
    grouped = _group_records(records)
    if len(grouped) < 3:
        raise ValueError("at least three groups are required")
    rng = np.random.default_rng(seed)
    groups = list(grouped)
    rng.shuffle(groups)

    targets = np.asarray(
        [train_fraction, validation_fraction, 1.0 - train_fraction - validation_fraction]
    ) * len(records)
    assignments: list[list[str]] = [[], [], []]
    counts = np.zeros(3, dtype=float)
    # Large and label-rare groups are assigned first to reduce imbalance drift.
    label_frequency = Counter(record.label for record in records)
    groups.sort(
        key=lambda group: (
            -len(grouped[group]),
            min(label_frequency[record.label] for record in grouped[group]),
            group,
        )
    )
    for group in groups:
        size = len(grouped[group])
        deficits = targets - counts
        split_index = int(np.argmax(deficits / np.maximum(targets, 1)))
        assignments[split_index].append(group)
        counts[split_index] += size
    if any(not groups_in_split for groups_in_split in assignments):
        raise RuntimeError("group allocation produced an empty split")
    return RecordSplit(
        train=tuple(_records_for_groups(grouped, assignments[0])),
        validation=tuple(_records_for_groups(grouped, assignments[1])),
        test=tuple(_records_for_groups(grouped, assignments[2])),
    )


def cross_condition_split(
    records: Sequence[SignalRecord],
    *,
    train_conditions: Iterable[str],
    test_conditions: Iterable[str],
    seed: int,
    validation_fraction: float = 0.2,
) -> RecordSplit:
    train_conditions = set(train_conditions)
    test_conditions = set(test_conditions)
    if not train_conditions or not test_conditions or train_conditions.intersection(test_conditions):
        raise ValueError("train and test conditions must be non-empty and disjoint")
    source = [record for record in records if record.condition in train_conditions]
    target = [record for record in records if record.condition in test_conditions]
    if not source or not target:
        raise ValueError("requested conditions do not yield source and target records")
    grouped = _group_records(source)
    if len(grouped) < 2:
        raise ValueError("at least two source-domain groups are required")
    groups = list(grouped)
    np.random.default_rng(seed).shuffle(groups)
    validation_count = max(1, min(len(groups) - 1, int(round(len(groups) * validation_fraction))))
    validation_groups = groups[:validation_count]
    train_groups = groups[validation_count:]
    return RecordSplit(
        train=tuple(_records_for_groups(grouped, train_groups)),
        validation=tuple(_records_for_groups(grouped, validation_groups)),
        test=tuple(target),
    )


def chronological_record_split(
    records: Sequence[SignalRecord],
    *,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> RecordSplit:
    if any(record.timestamp is None for record in records):
        raise ValueError("every record needs timestamp for chronological split")
    grouped = _group_records(records)
    ordered_groups = sorted(
        grouped,
        key=lambda group: min(float(record.timestamp) for record in grouped[group]),
    )
    n = len(ordered_groups)
    train_stop = max(1, int(np.floor(n * train_fraction)))
    validation_stop = max(train_stop + 1, int(np.floor(n * (train_fraction + validation_fraction))))
    if validation_stop >= n:
        raise ValueError("not enough chronological groups for three splits")
    return RecordSplit(
        train=tuple(_records_for_groups(grouped, ordered_groups[:train_stop])),
        validation=tuple(_records_for_groups(grouped, ordered_groups[train_stop:validation_stop])),
        test=tuple(_records_for_groups(grouped, ordered_groups[validation_stop:])),
    )


def assert_no_group_leakage(split: RecordSplit) -> None:
    groups = [
        {record.group_id for record in split.train},
        {record.group_id for record in split.validation},
        {record.group_id for record in split.test},
    ]
    if groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2]:
        raise ValueError("group_id leakage across train/validation/test")


def _group_records(records: Sequence[SignalRecord]) -> dict[str, list[SignalRecord]]:
    result: dict[str, list[SignalRecord]] = defaultdict(list)
    for record in records:
        result[record.group_id].append(record)
    return dict(result)


def _records_for_groups(
    grouped: dict[str, list[SignalRecord]], groups: Iterable[str]
) -> list[SignalRecord]:
    return [record for group in groups for record in grouped[group]]
