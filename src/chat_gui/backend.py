"""Testable backend for chat-gui."""
from typing import Optional
from dataclasses import dataclass
from chat_lib import CatgirlPipeline, PipelineConfig


@dataclass
class Message:
    """Represents a possible cat-girl message."""
    text: str
    mood: str
    kaomoji: str
    action: str
    suffix: str

    def display(self) -> str:
        """Format message for display."""
        parts = []
        if self.action:
            parts.append(f"*{self.action}*")
        if self.text:
            parts.append(self.text)
        if self.suffix:
            parts.append(self.suffix)
        if self.kaomoji:
            parts.append(self.kaomoji)
        return " ".join(parts)


class ChatBackend:
    """Testable backend for cat-girl chat transformation."""

    def __init__(self, backend: str = "mock", model: Optional[str] = None):
        config = PipelineConfig.default()
        config.llm.backend = backend
        if model:
            config.llm.model = model
        self.pipeline = CatgirlPipeline(config)

    async def transform(self, text: str, n_variants: int = 3) -> list[Message]:
        """Transform text into multiple cat-girl message variants.

        Args:
            text: Input text to transform
            n_variants: Number of message variants to generate

        Returns:
            List of Message objects representing possible responses
        """
        messages = []
        for _ in range(n_variants):
            state = await self.pipeline.transform_full(text)
            msg = Message(
                text=state.get("styled_text", ""),
                mood=state.get("mood", "neutral"),
                kaomoji=state.get("kaomoji", ""),
                action=state.get("action", ""),
                suffix=state.get("suffix", ""),
            )
            messages.append(msg)
        return messages
