from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter


class LatencyTracker:
    """Collects named step latencies within a single logical operation.

    Usage::

        tracker = LatencyTracker("send_message")
        async with tracker.step("retrieval"):
            ...
        tracker.record("llm_generation", elapsed_ms)
        tracker.log_summary(logger, extra={"conversation_id": str(cid)})
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._steps: list[tuple[str, float]] = []
        self._started_at = perf_counter()

    @asynccontextmanager
    async def step(self, name: str) -> AsyncIterator[None]:
        started = perf_counter()
        try:
            yield
        finally:
            self._steps.append((name, (perf_counter() - started) * 1000.0))

    def record(self, name: str, duration_ms: float) -> None:
        self._steps.append((name, duration_ms))

    @property
    def total_ms(self) -> float:
        return (perf_counter() - self._started_at) * 1000.0

    @property
    def steps_ms(self) -> dict[str, float]:
        aggregated: dict[str, float] = {}
        for name, ms in self._steps:
            aggregated[name] = aggregated.get(name, 0.0) + ms
        return aggregated

    def log_summary(
        self,
        logger: logging.Logger,
        level: int = logging.INFO,
        extra: dict[str, object] | None = None,
    ) -> None:
        payload: dict[str, object] = {
            "event": "latency_summary",
            "operation": self._name,
            "total_ms": round(self.total_ms, 2),
            "steps_ms": {name: round(ms, 2) for name, ms in self.steps_ms.items()},
        }
        if extra:
            payload.update(extra)
        logger.log(level, "latency_summary operation=%s", self._name, extra=payload)
