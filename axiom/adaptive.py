"""Bounded, opt-in adaptive telemetry engine using an EMA baseline."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class AdaptiveSnapshot:
    samples_seen: int
    baseline: float | None
    recent_average: float | None
    trend: str


class AdaptiveEngine:
    """Tracks numeric observations without changing program semantics."""
    def __init__(self, alpha: float = 0.2, max_samples: int = 128):
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        if max_samples < 2:
            raise ValueError("max_samples must be >= 2")
        self.alpha = alpha
        self.samples = deque(maxlen=max_samples)
        self.baseline: float | None = None

    def observe(self, value: float) -> AdaptiveSnapshot:
        value = float(value)
        if not isfinite(value):
            raise ValueError("sample must be finite")
        previous = self.baseline
        self.baseline = value if previous is None else self.alpha * value + (1 - self.alpha) * previous
        self.samples.append(value)
        recent = sum(self.samples) / len(self.samples)
        trend = "steady" if previous is None or value == previous else ("up" if value > previous else "down")
        return AdaptiveSnapshot(len(self.samples), self.baseline, recent, trend)

    def reset(self) -> None:
        self.samples.clear()
        self.baseline = None
