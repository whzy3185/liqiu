"""Compact time, frequency, and envelope features for vibration signals."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import hilbert
from scipy.stats import kurtosis, skew


EPS = 1e-12


@dataclass(frozen=True)
class FeatureConfig:
    frequency_bands: int = 4
    top_spectral_peaks: int = 3
    include_wavelet_packet: bool = False
    wavelet: str = "db4"
    wavelet_level: int = 3

    def __post_init__(self) -> None:
        if self.frequency_bands < 2 or self.top_spectral_peaks < 1:
            raise ValueError("frequency_bands >= 2 and top_spectral_peaks >= 1 are required")
        if self.wavelet_level < 1:
            raise ValueError("wavelet_level must be positive")


def extract_features(
    signal: np.ndarray,
    sampling_rate: float,
    config: FeatureConfig = FeatureConfig(),
) -> tuple[np.ndarray, list[str]]:
    signal = np.asarray(signal, dtype=float)
    if signal.ndim == 1:
        signal = signal[None, :]
    if signal.ndim != 2 or signal.shape[1] < 8:
        raise ValueError("signal must have shape (channels, samples >= 8)")
    if not np.isfinite(signal).all() or sampling_rate <= 0:
        raise ValueError("signal must be finite and sampling_rate positive")

    values: list[float] = []
    names: list[str] = []
    for channel, series in enumerate(signal):
        channel_values, channel_names = _channel_features(series, sampling_rate, config)
        values.extend(channel_values)
        names.extend([f"ch{channel}_{name}" for name in channel_names])
    if len(values) > 120:
        raise ValueError(
            f"feature dimension {len(values)} exceeds the 120-feature scout cap; select fewer channels"
        )
    array = np.asarray(values, dtype=float)
    if not np.isfinite(array).all():
        raise RuntimeError("feature extraction produced non-finite values")
    return array, names


def _channel_features(x: np.ndarray, fs: float, config: FeatureConfig) -> tuple[list[float], list[str]]:
    mean = float(np.mean(x))
    centered = x - mean
    std = float(np.std(x))
    variance = float(np.var(x))
    rms = float(np.sqrt(np.mean(x * x)))
    absolute = np.abs(x)
    mean_abs = float(np.mean(absolute))
    peak = float(np.max(absolute))
    sqrt_abs_mean = float(np.mean(np.sqrt(absolute)))
    margin = peak / (sqrt_abs_mean**2 + EPS)
    time_values = [
        mean,
        std,
        variance,
        rms,
        peak,
        float(np.ptp(x)),
        _finite_stat(skew(x, bias=False)),
        _finite_stat(kurtosis(x, fisher=False, bias=False)),
        peak / (rms + EPS),
        rms / (mean_abs + EPS),
        peak / (mean_abs + EPS),
        margin,
        margin,
        float(np.sum(x * x)),
        float(np.mean(np.signbit(centered[1:]) != np.signbit(centered[:-1]))),
    ]
    time_names = [
        "mean",
        "std",
        "variance",
        "rms",
        "peak",
        "peak_to_peak",
        "skewness",
        "kurtosis",
        "crest_factor",
        "shape_factor",
        "impulse_factor",
        "clearance_factor",
        "margin_factor",
        "energy",
        "zero_crossing_rate",
    ]

    frequencies = np.fft.rfftfreq(len(x), d=1.0 / fs)
    spectrum = np.abs(np.fft.rfft(centered))
    power = spectrum * spectrum
    if len(power) > 1:
        power[0] = 0.0
    total_power = float(power.sum()) + EPS
    probability = power / total_power
    dominant_index = int(np.argmax(power))
    centroid = float(np.sum(frequencies * probability))
    spread = float(np.sqrt(np.sum(((frequencies - centroid) ** 2) * probability)))
    spectral_rms = float(np.sqrt(np.sum((frequencies**2) * probability)))
    nonzero_probability = probability[probability > 0]
    entropy = float(-np.sum(nonzero_probability * np.log(nonzero_probability)))
    entropy /= float(np.log(max(len(probability), 2)))
    frequency_values = [float(frequencies[dominant_index]), centroid, spread, spectral_rms, entropy]
    frequency_names = [
        "dominant_frequency",
        "spectral_centroid",
        "spectral_spread",
        "spectral_rms",
        "spectral_entropy",
    ]

    band_edges = np.linspace(0, len(power), config.frequency_bands + 1, dtype=int)
    for band in range(config.frequency_bands):
        band_power = float(power[band_edges[band] : band_edges[band + 1]].sum() / total_power)
        frequency_values.append(band_power)
        frequency_names.append(f"band_energy_{band}")

    candidates = np.argsort(power[1:])[::-1] + 1 if len(power) > 1 else np.array([0])
    peak_indices = list(candidates[: config.top_spectral_peaks])
    while len(peak_indices) < config.top_spectral_peaks:
        peak_indices.append(0)
    for rank, index in enumerate(peak_indices):
        frequency_values.extend([float(frequencies[index]), float(power[index] / total_power)])
        frequency_names.extend([f"spectral_peak_{rank}_frequency", f"spectral_peak_{rank}_energy"])
    midpoint = max(1, len(power) // 2)
    low = float(power[:midpoint].sum())
    high = float(power[midpoint:].sum())
    frequency_values.append(high / (low + EPS))
    frequency_names.append("high_low_frequency_energy_ratio")

    envelope = np.abs(hilbert(centered))
    envelope_centered = envelope - envelope.mean()
    envelope_spectrum = np.abs(np.fft.rfft(envelope_centered)) ** 2
    envelope_values = [
        float(envelope.mean()),
        float(np.sqrt(np.mean(envelope * envelope))),
        _finite_stat(kurtosis(envelope, fisher=False, bias=False)),
        float(envelope_spectrum.sum() / max(len(envelope), 1)),
    ]
    envelope_names = [
        "envelope_mean",
        "envelope_rms",
        "envelope_kurtosis",
        "envelope_spectral_energy",
    ]

    wavelet_values: list[float] = []
    wavelet_names: list[str] = []
    if config.include_wavelet_packet:
        try:
            import pywt
        except ImportError as exc:
            raise ImportError("PyWavelets is required when include_wavelet_packet=True") from exc
        packet = pywt.WaveletPacket(centered, wavelet=config.wavelet, maxlevel=config.wavelet_level)
        nodes = packet.get_level(config.wavelet_level, order="freq")
        energies = np.asarray([np.sum(np.asarray(node.data) ** 2) for node in nodes], dtype=float)
        energies /= energies.sum() + EPS
        wavelet_values.extend(energies.tolist())
        wavelet_names.extend([f"wavelet_packet_energy_{index}" for index in range(len(nodes))])

    return (
        time_values + frequency_values + envelope_values + wavelet_values,
        time_names + frequency_names + envelope_names + wavelet_names,
    )


def _finite_stat(value: float) -> float:
    return float(value) if np.isfinite(value) else 0.0

