"""Configuration-driven experiment execution and append-only record keeping."""

from __future__ import annotations

import contextlib
import datetime as dt
import fcntl
import hashlib
import importlib
import json
import os
import platform
import random
import resource
import subprocess
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Mapping


ALLOWED_INITIAL_SEEDS = (1, 7, 21, 42, 2026)
VALID_POOLS = {"exploration", "confirmation"}
REQUIRED_RESULT_KEYS = {
    "metrics",
    "structure",
    "notes",
}


class ConfigurationError(ValueError):
    """Raised when a run violates the research protocol."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _config_hash(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(config).encode("utf-8")).hexdigest()[:12]


def _git_state(repo: Path) -> Dict[str, Any]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
        ).stdout.strip())
        return {"commit": commit, "dirty": dirty}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"commit": "NO_COMMIT", "dirty": True}


def _peak_memory_mb() -> float:
    value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # macOS reports bytes; Linux reports KiB.
    return value / (1024.0 * 1024.0) if platform.system() == "Darwin" else value / 1024.0


def _validate_config(config: Mapping[str, Any]) -> None:
    for key in ("algorithm", "dataset", "pool", "seed", "runner"):
        if key not in config:
            raise ConfigurationError(f"missing required config key: {key}")
    if config["pool"] not in VALID_POOLS:
        raise ConfigurationError(f"pool must be one of {sorted(VALID_POOLS)}")
    if not isinstance(config["seed"], int):
        raise ConfigurationError("seed must be an integer")
    if not config.get("claim_validation", False) and config["seed"] not in ALLOWED_INITIAL_SEEDS:
        raise ConfigurationError(
            f"initial seed must be one of {ALLOWED_INITIAL_SEEDS}; set claim_validation=true "
            "only when deliberately adding confirmatory seeds"
        )
    if config["pool"] == "confirmation":
        if not str(config.get("confirmation_rationale", "")).strip():
            raise ConfigurationError("confirmation runs require confirmation_rationale")
        if config.get("search", {}).get("enabled", False):
            raise ConfigurationError("hyperparameter search is forbidden on the confirmation pool")
    runner = config["runner"]
    if not isinstance(runner, str) or ":" not in runner:
        raise ConfigurationError("runner must use 'module.path:function' syntax")


def _load_runner(spec: str):
    module_name, function_name = spec.split(":", 1)
    function = getattr(importlib.import_module(module_name), function_name)
    if not callable(function):
        raise ConfigurationError(f"runner is not callable: {spec}")
    return function


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def run_from_config(config_path: Path, output_path: Path) -> Dict[str, Any]:
    """Run one configured experiment and append a complete success/failure record."""
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    _validate_config(config)

    repo = Path(__file__).resolve().parents[1]
    seed = int(config["seed"])
    random.seed(seed)
    with contextlib.suppress(ImportError):
        import numpy as np
        np.random.seed(seed)

    started = dt.datetime.now(dt.timezone.utc)
    started_clock = time.perf_counter()
    git = _git_state(repo)
    digest = _config_hash(config)
    experiment_id = config.get("experiment_id") or f"{started.strftime('%Y%m%dT%H%M%SZ')}-{digest}"

    base: Dict[str, Any] = {
        "schema_version": "1.0",
        "experiment_id": experiment_id,
        "git_commit": git["commit"],
        "git_dirty": git["dirty"],
        "date_utc": started.isoformat(),
        "config_path": str(config_path.relative_to(repo)) if repo in config_path.parents else str(config_path),
        "config_sha256_12": digest,
        "algorithm": config["algorithm"],
        "dataset": config["dataset"],
        "dataset_generation_parameters": config.get("dataset_generation_parameters", {}),
        "pool": config["pool"],
        "seed": seed,
        "hyperparameters": config.get("hyperparameters", {}),
    }

    try:
        result = _load_runner(config["runner"])(config)
        missing = REQUIRED_RESULT_KEYS.difference(result)
        if missing:
            raise RuntimeError(f"runner result missing keys: {sorted(missing)}")
        base.update({
            "accuracy": result["metrics"].get("accuracy"),
            "macro_f1": result["metrics"].get("macro_f1"),
            "auroc": result["metrics"].get("auroc"),
            "calibration_error": result["metrics"].get("calibration_error"),
            "additional_metrics": result["metrics"].get("additional", {}),
            "granule_count": result["structure"].get("granule_count"),
            "average_granule_size": result["structure"].get("average_granule_size"),
            "uncertain_sample_ratio": result["structure"].get("uncertain_sample_ratio"),
            "structure": result["structure"].get("additional", {}),
            "outcome": result.get("outcome", "success"),
            "notes": result["notes"],
            "error": None,
        })
    except Exception as exc:  # Failure records are intentionally persisted.
        base.update({
            "accuracy": None, "macro_f1": None, "auroc": None,
            "calibration_error": None, "additional_metrics": {},
            "granule_count": None, "average_granule_size": None,
            "uncertain_sample_ratio": None, "structure": {},
            "outcome": "failure",
            "notes": "Runner raised an exception; traceback retained in record.",
            "error": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()},
        })

    base["runtime_seconds"] = round(time.perf_counter() - started_clock, 6)
    base["peak_memory_mb"] = round(_peak_memory_mb(), 3)
    _append_jsonl(output_path.resolve(), base)
    return base

