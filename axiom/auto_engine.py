"""Execution wrapper with optional bounded timing telemetry."""
from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Any
from .adaptive import AdaptiveEngine, AdaptiveSnapshot
from .compiler import run


@dataclass(frozen=True)
class RunReport:
    results: list[Any]
    elapsed_seconds: float
    adaptation: AdaptiveSnapshot | None


class AutoEngine:
    """Runs Axiom source and optionally observes execution duration."""
    def __init__(self, telemetry: bool = False, alpha: float = 0.2, max_samples: int = 128):
        self.adaptive = AdaptiveEngine(alpha=alpha, max_samples=max_samples) if telemetry else None

    def execute(self, source: str, output=print) -> RunReport:
        start = perf_counter()
        results = run(source, output=output)
        elapsed = perf_counter() - start
        snapshot = self.adaptive.observe(elapsed) if self.adaptive else None
        return RunReport(results, elapsed, snapshot)
