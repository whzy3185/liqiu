"""Data contracts and recording-level segmentation for fault diagnosis."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class SignalRecord:
    """One indivisible acquisition record.

    `group_id` is the minimum leakage unit. Every window derived from this
    record, and from any related record assigned the same group, stays in one
    split. Use a physical bearing/machine ID when available; otherwise use the
    original acquisition-file/session ID.
    """

    signal: np.ndarray
    label: Any
    group_id: str
    sampling_rate: float
    record_id: str
    unit_id: str | None = None
    condition: str | None = None
    timestamp: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        signal = np.asarray(self.signal, dtype=float)
        if signal.ndim == 1:
            signal = signal[None, :]
        if signal.ndim != 2 or signal.shape[1] < 2:
            raise ValueError("signal must have shape (channels, samples) with at least two samples")
        if not np.isfinite(signal).all():
            raise ValueError("signal contains non-finite values")
        if self.sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive")
        if not self.group_id or not self.record_id:
            raise ValueError("group_id and record_id are required")
        object.__setattr__(self, "signal", signal)


@dataclass(frozen=True)
class SignalWindow:
    signal: np.ndarray
    label: Any
    group_id: str
    record_id: str
    unit_id: str | None
    condition: str | None
    sampling_rate: float
    start: int
    stop: int


@dataclass(frozen=True)
class WindowConfig:
    size: int
    step: int
    channels: tuple[int, ...] = (0,)
    include_tail: bool = False

    def __post_init__(self) -> None:
        if self.size < 8 or self.step < 1:
            raise ValueError("window size must be >= 8 and step must be positive")
        if not self.channels or min(self.channels) < 0:
            raise ValueError("at least one non-negative channel is required")


def segment_record(record: SignalRecord, config: WindowConfig) -> list[SignalWindow]:
    if max(config.channels) >= record.signal.shape[0]:
        raise ValueError(f"record {record.record_id} does not contain requested channels {config.channels}")
    n = record.signal.shape[1]
    if n < config.size:
        return []
    starts = list(range(0, n - config.size + 1, config.step))
    if config.include_tail and starts[-1] != n - config.size:
        starts.append(n - config.size)
    return [
        SignalWindow(
            signal=record.signal[np.asarray(config.channels), start : start + config.size],
            label=record.label,
            group_id=record.group_id,
            record_id=record.record_id,
            unit_id=record.unit_id,
            condition=record.condition,
            sampling_rate=record.sampling_rate,
            start=start,
            stop=start + config.size,
        )
        for start in starts
    ]


def load_npz_records(path: str | Path) -> list[SignalRecord]:
    """Load a source-neutral record bundle.

    Required arrays are `signals`, `labels`, `group_ids`, `record_ids`, and
    `sampling_rates`. Signals may be an object array when record lengths differ.
    Optional arrays are `unit_ids`, `conditions`, and `timestamps`.
    Dataset-specific adapters should normalize their raw format into this
    contract without segmenting.
    """
    path = Path(path)
    with np.load(path, allow_pickle=True) as bundle:
        required = {"signals", "labels", "group_ids", "record_ids", "sampling_rates"}
        missing = required.difference(bundle.files)
        if missing:
            raise ValueError(f"missing arrays in {path}: {sorted(missing)}")
        count = len(bundle["labels"])
        for key in required:
            if len(bundle[key]) != count:
                raise ValueError(f"array {key} has inconsistent length")
        optional = {
            "unit_ids": np.full(count, None, dtype=object),
            "conditions": np.full(count, None, dtype=object),
            "timestamps": np.full(count, None, dtype=object),
        }
        for key in optional:
            if key in bundle.files:
                optional[key] = bundle[key]
        return [
            SignalRecord(
                signal=bundle["signals"][i],
                label=bundle["labels"][i].item() if hasattr(bundle["labels"][i], "item") else bundle["labels"][i],
                group_id=str(bundle["group_ids"][i]),
                record_id=str(bundle["record_ids"][i]),
                sampling_rate=float(bundle["sampling_rates"][i]),
                unit_id=None if optional["unit_ids"][i] is None else str(optional["unit_ids"][i]),
                condition=None if optional["conditions"][i] is None else str(optional["conditions"][i]),
                timestamp=None if optional["timestamps"][i] is None else float(optional["timestamps"][i]),
            )
            for i in range(count)
        ]


def records_by_id(records: Sequence[SignalRecord]) -> dict[str, SignalRecord]:
    result: dict[str, SignalRecord] = {}
    for record in records:
        if record.record_id in result:
            raise ValueError(f"duplicate record_id: {record.record_id}")
        result[record.record_id] = record
    return result

