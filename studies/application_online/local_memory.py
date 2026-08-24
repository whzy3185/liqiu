"""Fixed-budget local ball memory with matched streaming controls."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, f1_score, recall_score

from baselines.gbc import GranularBallClassifier
from counterexamples.generators import generate_stream


@dataclass
class OnlineBall:
    center: np.ndarray
    radius: float
    counts: np.ndarray
    weight: float
    last_seen: int

    @property
    def label(self) -> int:
        return int(np.argmax(self.counts))


class OnlineBallMemory:
    def __init__(self, classes: np.ndarray, max_balls: int = 24, alpha: float = 0.35):
        self.classes = np.asarray(classes)
        self.max_balls = max_balls
        self.alpha = alpha
        self.balls: list[OnlineBall] = []

    def fit(self, features: np.ndarray, labels: np.ndarray):
        self.balls = []
        for label in self.classes:
            local = features[labels == label]
            if len(local) == 0:
                continue
            center = local.mean(axis=0)
            radius = max(float(np.quantile(np.linalg.norm(local - center, axis=1), 0.95)), 1e-6)
            counts = np.zeros(len(self.classes), dtype=float)
            counts[int(label)] = len(local)
            self.balls.append(OnlineBall(center, radius, counts, float(len(local)), 0))
        return self

    def _distances(self, features: np.ndarray, surface: bool) -> np.ndarray:
        centers = np.vstack([ball.center for ball in self.balls])
        distances = np.linalg.norm(features[:, None, :] - centers[None, :, :], axis=2)
        if surface:
            radii = np.asarray([ball.radius for ball in self.balls])
            distances = (distances - radii[None, :]) / radii[None, :]
        return distances

    def predict(self, features: np.ndarray, surface: bool) -> np.ndarray:
        assigned = np.argmin(self._distances(features, surface), axis=1)
        return np.asarray([self.balls[index].label for index in assigned])

    def _merge_to_budget(self):
        while len(self.balls) > self.max_balls:
            pairs = []
            for left in range(len(self.balls)):
                for right in range(left + 1, len(self.balls)):
                    if self.balls[left].label == self.balls[right].label:
                        distance = float(
                            np.linalg.norm(self.balls[left].center - self.balls[right].center)
                        )
                        pairs.append((distance, left, right))
            if not pairs:
                victim = min(range(len(self.balls)), key=lambda index: self.balls[index].weight)
                self.balls.pop(victim)
                continue
            _, left, right = min(pairs)
            first, second = self.balls[left], self.balls[right]
            total = first.weight + second.weight
            center = (first.weight * first.center + second.weight * second.center) / total
            radius = max(
                first.radius + float(np.linalg.norm(first.center - center)),
                second.radius + float(np.linalg.norm(second.center - center)),
            )
            merged = OnlineBall(
                center,
                radius,
                first.counts + second.counts,
                total,
                max(first.last_seen, second.last_seen),
            )
            self.balls.pop(right)
            self.balls.pop(left)
            self.balls.append(merged)

    def update(self, features: np.ndarray, labels: np.ndarray, step: int):
        distances = self._distances(features, surface=False)
        assigned = np.argmin(distances, axis=1)
        novel = np.zeros(len(features), dtype=bool)
        for row, ball_index in enumerate(assigned):
            ball = self.balls[int(ball_index)]
            novel[row] = ball.label != int(labels[row]) or distances[row, ball_index] > 1.5 * ball.radius

        for ball_index, ball in enumerate(self.balls):
            selected = (assigned == ball_index) & ~novel
            if not selected.any():
                ball.counts *= 0.97
                ball.weight *= 0.97
                continue
            local = features[selected]
            center = local.mean(axis=0)
            radius = max(float(np.quantile(np.linalg.norm(local - center, axis=1), 0.95)), 1e-6)
            ball.center = (1 - self.alpha) * ball.center + self.alpha * center
            ball.radius = (1 - self.alpha) * ball.radius + self.alpha * radius
            ball.counts = (1 - self.alpha) * ball.counts + self.alpha * np.bincount(
                labels[selected], minlength=len(self.classes)
            )
            ball.weight = (1 - self.alpha) * ball.weight + self.alpha * selected.sum()
            ball.last_seen = step

        for label in self.classes:
            local = features[novel & (labels == label)]
            if len(local) < 5:
                continue
            center = local.mean(axis=0)
            radius = max(float(np.quantile(np.linalg.norm(local - center, axis=1), 0.95)), 1e-6)
            counts = np.zeros(len(self.classes), dtype=float)
            counts[int(label)] = len(local)
            self.balls.append(OnlineBall(center, radius, counts, float(len(local)), step))

        keep = []
        for label in self.classes:
            same_class = [ball for ball in self.balls if ball.label == int(label)]
            if not same_class:
                continue
            recent = [ball for ball in same_class if step - ball.last_seen <= 3]
            keep.extend(recent or [max(same_class, key=lambda ball: ball.weight)])
        self.balls = keep
        self._merge_to_budget()

    @property
    def memory_bytes(self) -> int:
        if not self.balls:
            return 0
        dimension = len(self.balls[0].center)
        floats_per_ball = dimension + len(self.classes) + 3
        return int(len(self.balls) * floats_per_ball * 8)


def _metrics(labels, prediction, emerging=False):
    output = {
        "accuracy": float(accuracy_score(labels, prediction)),
        "macro_f1": float(f1_score(labels, prediction, average="macro", zero_division=0)),
    }
    if emerging and np.any(labels == 2):
        output["emerging_recall"] = float(
            recall_score(labels, prediction, labels=[2], average="macro", zero_division=0)
        )
    return output


def evaluate_online_memory(kind: str, seed: int, max_balls: int = 24):
    features, labels, times, _ = generate_stream(
        kind, n_steps=10, samples_per_step=200, seed=seed, ambient_dimension=5, drift_strength=2.0
    )
    classes = np.array([0, 1, 2]) if kind == "emerging_class" else np.array([0, 1])
    first = times == 0
    memory = OnlineBallMemory(classes, max_balls=max_balls).fit(features[first], labels[first])
    sliding = GranularBallClassifier(0.85).fit(features[first], labels[first])
    sgd = SGDClassifier(loss="log_loss", random_state=seed).partial_fit(
        features[first], labels[first], classes=classes
    )
    history_x = [features[first]]
    history_y = [labels[first]]
    batch_metrics = {method: [] for method in ("gb_surface", "center_ablation", "sliding_gbc", "sgd")}
    update_seconds = {method: 0.0 for method in ("local_memory", "sliding_gbc", "sgd")}
    ball_counts = []
    memory_bytes = []
    for step in range(1, 10):
        mask = times == step
        current_x, current_y = features[mask], labels[mask]
        predictions = {
            "gb_surface": memory.predict(current_x, surface=True),
            "center_ablation": memory.predict(current_x, surface=False),
            "sliding_gbc": sliding.predict(current_x),
            "sgd": sgd.predict(current_x),
        }
        for method, prediction in predictions.items():
            batch_metrics[method].append(
                {"step": step, **_metrics(current_y, prediction, kind == "emerging_class")}
            )

        start = time.perf_counter()
        memory.update(current_x, current_y, step)
        update_seconds["local_memory"] += time.perf_counter() - start
        ball_counts.append(len(memory.balls))
        memory_bytes.append(memory.memory_bytes)

        history_x.append(current_x)
        history_y.append(current_y)
        start = time.perf_counter()
        sliding = GranularBallClassifier(0.85).fit(
            np.vstack(history_x[-3:]), np.concatenate(history_y[-3:])
        )
        update_seconds["sliding_gbc"] += time.perf_counter() - start
        start = time.perf_counter()
        sgd.partial_fit(current_x, current_y)
        update_seconds["sgd"] += time.perf_counter() - start

    summary = {}
    for method, rows in batch_metrics.items():
        emerging = [row["emerging_recall"] for row in rows if "emerging_recall" in row]
        summary[method] = {
            "accuracy": float(np.mean([row["accuracy"] for row in rows])),
            "macro_f1": float(np.mean([row["macro_f1"] for row in rows])),
            "emerging_recall": float(np.mean(emerging)) if emerging else None,
            "batch_metrics": rows,
        }
    summary["gb_surface"]["mean_update_seconds"] = update_seconds["local_memory"] / 9
    summary["center_ablation"]["mean_update_seconds"] = update_seconds["local_memory"] / 9
    summary["sliding_gbc"]["mean_update_seconds"] = update_seconds["sliding_gbc"] / 9
    summary["sgd"]["mean_update_seconds"] = update_seconds["sgd"] / 9
    return {
        "methods": summary,
        "mean_balls": float(np.mean(ball_counts)),
        "max_balls": int(max(ball_counts)),
        "mean_memory_bytes": float(np.mean(memory_bytes)),
        "max_memory_bytes": int(max(memory_bytes)),
    }
