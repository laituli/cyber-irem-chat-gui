"""Testable backend for chat-gui."""
import random
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from chat_lib import CatgirlPipeline, PipelineConfig


EMOTES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "emotes" / "data" / "user_given"


@dataclass
class Message:
    """Represents a possible cat-girl message."""
    text: str
    mood: str
    kaomoji: str
    action: str
    suffix: str
    emote: str = ""

    def display(self) -> str:
        """Format message for display: action + text + suffix + kaomoji."""
        parts = []
        if self.action:
            parts.append(self.action)
        if self.text:
            parts.append(self.text)
        if self.suffix:
            parts.append(self.suffix)
        if self.kaomoji:
            parts.append(self.kaomoji)
        return " ".join(parts)


def _pick_emote() -> str:
    """Pick a random emote image path if available."""
    if EMOTES_DIR.exists():
        images = [f for f in EMOTES_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")]
        if images:
            return str(random.choice(images))
    return ""


class ChatBackend:
    """Testable backend for cat-girl chat transformation."""

    def __init__(self, backend: str = "mock", model: Optional[str] = None):
        config = PipelineConfig.default()
        config.llm.backend = backend
        if model:
            config.llm.model = model
        self.pipeline = CatgirlPipeline(config)

    async def transform(self, text: str, n_variants: int = 3) -> list[Message]:
        """Transform text into multiple cat-girl message variants."""
        messages = []
        for _ in range(n_variants):
            state = await self.pipeline.transform_full(text)
            msg = Message(
                text=state.get("styled_text", ""),
                mood=state.get("mood", "neutral"),
                kaomoji=state.get("kaomoji", ""),
                action=state.get("action", ""),
                suffix=state.get("suffix", ""),
                emote=_pick_emote(),
            )
            messages.append(msg)
        return messages
