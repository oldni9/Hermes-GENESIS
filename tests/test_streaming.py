"""
===============================================================================
Tests for Chat streaming through AIPipeline (Sprint 3 PR3)

Verifies:
    - Chat.stream() uses pipeline.stream() when pipeline is provided.
    - Chat.stream() falls back to manager simulation when pipeline is None.
    - Streaming chunks are yielded correctly.
    - Final response is returned correctly.
    - Conversation receives deltas.
    - Early closure cleans up the pipeline generator.
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.ai.chat import Chat
from hermes.ai.manager import AIManager
from hermes.ai.pipeline import AIPipeline
from hermes.ai.response import (
    AIResponse,
    ResponseChunk,
    ResponseChoice,
    ResponseMessage,
)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def make_chunk(content: str, finish_reason: str | None = None) -> ResponseChunk:
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=content),
        finish_reason=finish_reason,
    )
    return ResponseChunk(
        id="test-id",
        created=12345,
        model="test-model",
        choices=[choice],
        finish_reason=finish_reason,
    )


def pipeline_generator():
    """Real generator that mimics pipeline.stream() with return value."""
    yield make_chunk("Hello ")
    yield make_chunk("world")
    return AIResponse(success=True, result="Hello world", provider="test", model="test")


def pipeline_generator_with_error():
    yield make_chunk("Hello")
    raise ValueError("Stream error")


def pipeline_generator_with_cancel(closed_flag: list[bool]):
    """Generator that sets a flag when close() is called."""
    try:
        yield make_chunk("Hello")
        while True:
            yield make_chunk("chunk")
    except GeneratorExit:
        closed_flag[0] = True
        raise


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


def test_stream_uses_pipeline_when_provided() -> None:
    """Chat.stream() should use pipeline.stream() when pipeline is given."""
    pipeline = MagicMock(spec=AIPipeline)
    pipeline.stream.return_value = pipeline_generator()

    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(pipeline=pipeline, provider="test-provider", model="test-model")
        gen = chat.stream("Hello")
        chunks = []
        final = None
        it = gen
        while True:
            try:
                chunk = next(it)
                chunks.append(chunk)
            except StopIteration as e:
                final = e.value
                break

        assert len(chunks) == 2
        assert chunks[0].choices[0].message.content == "Hello "
        assert chunks[1].choices[0].message.content == "world"
        assert final is not None
        assert final.success is True
        assert final.text() == "Hello world"


def test_stream_falls_back_to_manager_when_no_pipeline() -> None:
    """Chat.stream() should use manager simulation when no pipeline."""
    manager = MagicMock(spec=AIManager)
    manager.execute.return_value = AIResponse(
        success=True,
        result="Hello world",
        provider="test",
        model="test",
        choices=[
            ResponseChoice(
                index=0,
                message=ResponseMessage(role="assistant", content="Hello world"),
            )
        ],
        finish_reason="stop",
    )
    chat = Chat(manager=manager, provider="test-provider", model="test-model")
    gen = chat.stream("Hello")
    chunks = list(gen)
    assert len(chunks) == 1
    assert chunks[0].choices[0].message.content == "Hello world"


def test_stream_appends_delta_to_conversation() -> None:
    """Conversation should receive deltas during streaming."""
    pipeline = MagicMock(spec=AIPipeline)
    pipeline.stream.return_value = pipeline_generator()

    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(pipeline=pipeline, provider="test-provider", model="test-model")
        gen = chat.stream("Hello")
        # Consume all chunks
        for _ in gen:
            pass
        # The conversation should have the accumulated text
        last_msg = chat._conversation._messages[-1]
        # Strip the leading space from the placeholder
        assert last_msg.content.strip() == "Hello world"


def test_stream_handles_error_cleanup() -> None:
    """If an error occurs, the stream should clean up and propagate."""
    pipeline = MagicMock(spec=AIPipeline)
    pipeline.stream.return_value = pipeline_generator_with_error()

    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(pipeline=pipeline, provider="test-provider", model="test-model")
        gen = chat.stream("Hello")
        with pytest.raises(ValueError, match="Stream error"):
            for _ in gen:
                pass
        # Streaming flag should be cleared
        assert chat._streaming_message_id is None


def test_stream_close_propagates() -> None:
    """Closing the generator should call close() on the underlying stream."""
    closed_flag = [False]

    def inner_generator():
        try:
            yield make_chunk("Hello")
            while True:
                yield make_chunk("chunk")
        except GeneratorExit:
            closed_flag[0] = True
            raise

    pipeline = MagicMock(spec=AIPipeline)
    pipeline.stream.return_value = inner_generator()

    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(pipeline=pipeline, provider="test-provider", model="test-model")
        gen = chat.stream("Hello")
        next(gen)  # start the generator
        gen.close()

        # Verify that the inner generator received GeneratorExit
        assert (
            closed_flag[0] is True
        ), "GeneratorExit was not propagated to inner generator"
