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
        """Format message for display: action + text + kaomoji.
        
        Clean format: (action) styled_text kaomoji
        Avoids duplicates and empty brackets.
        """
        parts = []
        
        # Action: ensure single parentheses, skip if empty
        if self.action and self.action.strip():
            action = self.action.strip()
            # Remove existing parentheses to avoid double-wrapping
            if action.startswith("(") and action.endswith(")"):
                action = action[1:-1]
            if action.startswith("（") and action.endswith("）"):
                action = action[1:-1]
            if action:
                parts.append(f"({action})")
        
        # Text: styled text
        if self.text and self.text.strip():
            parts.append(self.text.strip())
        
        # Kaomoji: skip if empty or just brackets
        if self.kaomoji and self.kaomoji.strip():
            kaomoji = self.kaomoji.strip()
            if kaomoji not in ("()", "（）", "( )"):
                parts.append(kaomoji)
        
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

    def __init__(self, backend: str = "ollama", model: Optional[str] = None, temperature: float = 0.8):
        config = PipelineConfig.default()
        config.llm.backend = backend
        config.llm.temperature = temperature
        if model:
            config.llm.model = model
        self.pipeline = CatgirlPipeline(config)

    async def transform(self, text: str, n_variants: int = 3, strategy: str = "standard") -> list[Message]:
        """Transform text into multiple cat-girl message variants."""
        messages = []
        for _ in range(n_variants):
            if strategy == "conservative":
                # Conservative: simple replacement without LLM text transformation
                state = await self._transform_conservative(text)
            else:
                state = await self.pipeline.transform_full(text, strategy=strategy)
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

    async def _transform_conservative(self, text: str) -> dict:
        """Conservative transformation: only replace pronouns, no LLM text rewrite."""
        # Simple pronoun replacement
        styled = text.replace("我", "本喵")
        if "你" in styled and "主人" not in styled:
            styled = styled.replace("你", "主人", 1)
        
        # Analyze mood (still use LLM for this)
        from chat_lib.prompts.irem_grammar import get_mood_analysis_prompt
        from chat_lib.llm.ollama import OllamaLLM
        llm = OllamaLLM(temperature=0.3)  # Low temperature for consistent mood
        mood_prompt = get_mood_analysis_prompt(text)
        mood_response = await llm.chat([{"role": "user", "content": mood_prompt}])
        mood = mood_response.strip().lower()
        valid_moods = {"happy", "sad", "surprised", "confused", "caring", "sleepy", "excited", "neutral"}
        if mood not in valid_moods:
            mood = "neutral"
        
        return {
            "styled_text": styled,
            "mood": mood,
            "kaomoji": "",
            "action": "",
            "suffix": "",
        }
