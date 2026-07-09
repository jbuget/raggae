import asyncio
import logging

import pytest

from raggae.application.services.latency_tracker import LatencyTracker


class TestLatencyTracker:
    @pytest.mark.asyncio
    async def test_step_records_measured_duration(self) -> None:
        tracker = LatencyTracker("op")

        async with tracker.step("phase-a"):
            await asyncio.sleep(0.01)

        steps = tracker.steps_ms
        assert "phase-a" in steps
        assert steps["phase-a"] >= 10.0

    @pytest.mark.asyncio
    async def test_multiple_steps_are_aggregated_by_name(self) -> None:
        tracker = LatencyTracker("op")

        async with tracker.step("phase-a"):
            await asyncio.sleep(0.005)
        async with tracker.step("phase-a"):
            await asyncio.sleep(0.005)
        async with tracker.step("phase-b"):
            await asyncio.sleep(0.005)

        steps = tracker.steps_ms
        assert steps["phase-a"] >= 10.0
        assert 0 < steps["phase-b"] < steps["phase-a"] + 5.0

    def test_record_accepts_precomputed_duration(self) -> None:
        tracker = LatencyTracker("op")

        tracker.record("external", 42.5)

        assert tracker.steps_ms["external"] == 42.5

    def test_total_ms_is_positive_after_creation(self) -> None:
        tracker = LatencyTracker("op")

        assert tracker.total_ms >= 0.0

    def test_log_summary_emits_structured_extra(self, caplog: pytest.LogCaptureFixture) -> None:
        tracker = LatencyTracker("send_message")
        tracker.record("retrieval", 12.3)
        tracker.record("llm", 456.7)

        logger = logging.getLogger("test.latency")
        with caplog.at_level(logging.INFO, logger="test.latency"):
            tracker.log_summary(logger, extra={"conversation_id": "abc"})

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.__dict__["event"] == "latency_summary"
        assert record.__dict__["operation"] == "send_message"
        assert record.__dict__["steps_ms"] == {"retrieval": 12.3, "llm": 456.7}
        assert record.__dict__["conversation_id"] == "abc"
        assert record.__dict__["total_ms"] >= 0.0
