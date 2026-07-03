"""Tests for chat-gui backend."""
import pytest
from chat_gui.backend import ChatBackend, Message


class TestMessage:
    """Tests for Message dataclass."""

    def test_display_full(self):
        msg = Message(
            text="你好",
            mood="happy",
            kaomoji="(^_^)",
            action="(挥手)",
            suffix="喵～"
        )
        result = msg.display()
        assert "(挥手)" in result
        assert "你好" in result
        assert "喵～" in result
        assert "(^_^)" in result

    def test_display_minimal(self):
        msg = Message(
            text="你好",
            mood="neutral",
            kaomoji="",
            action="",
            suffix=""
        )
        result = msg.display()
        assert result == "你好"

    def test_display_no_action_stars(self):
        msg = Message(text="你好", mood="neutral", kaomoji="", action="", suffix="")
        result = msg.display()
        assert "*" not in result


class TestChatBackend:
    """Tests for ChatBackend."""

    def test_init_mock(self):
        backend = ChatBackend(backend="mock")
        assert backend.pipeline is not None

    @pytest.mark.asyncio
    async def test_transform_mock(self):
        backend = ChatBackend(backend="mock")
        messages = await backend.transform("你好", n_variants=2)
        assert len(messages) == 2
        assert all(isinstance(m, Message) for m in messages)

    @pytest.mark.asyncio
    async def test_transform_single_variant(self):
        backend = ChatBackend(backend="mock")
        messages = await backend.transform("今天天气真好", n_variants=1)
        assert len(messages) == 1
        msg = messages[0]
        assert msg.text
        assert msg.mood == "happy"

    @pytest.mark.asyncio
    async def test_transform_returns_structured_fields(self):
        backend = ChatBackend(backend="mock")
        messages = await backend.transform("help", n_variants=1)
        msg = messages[0]
        assert msg.mood == "caring"
        assert msg.kaomoji != "" or msg.text != ""

    @pytest.mark.asyncio
    async def test_transform_empty_text(self):
        backend = ChatBackend(backend="mock")
        messages = await backend.transform("", n_variants=1)
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_emote_field_exists(self):
        backend = ChatBackend(backend="mock")
        messages = await backend.transform("你好", n_variants=1)
        msg = messages[0]
        assert hasattr(msg, "emote")
        assert isinstance(msg.emote, str)
