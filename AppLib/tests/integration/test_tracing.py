import pytest
from core.tracing import AsyncTracer

@pytest.mark.asyncio
async def test_span_noop():
    tracer = AsyncTracer("test", enabled=False)
    async with tracer.start_span("noop"):
        assert True  # Should not raise
