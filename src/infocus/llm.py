from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .config import ModelConfig


class LLMBackend(Protocol):
    """LLM interface used by the annotator."""

    async def complete(self, prompt: str, *, config: ModelConfig) -> str:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class OllamaBackend:
    """Minimal async client for a local Ollama server.

    The backend assumes the model is already pulled and loaded. We keep the
    payload small enough for 16GB GPUs (quantized checkpoints) and expose
    temperature/token options through :class:`ModelConfig`.
    """

    base_url: str = "http://localhost:11434"

    async def complete(self, prompt: str, *, config: ModelConfig) -> str:
        import httpx  # Imported lazily to keep tests running without the dependency.

        payload = {
            "model": config.llm_model,
            "prompt": prompt,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_new_tokens,
            },
            "stream": False,
        }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()


@dataclass(slots=True)
class StubBackend:
    """A deterministic backend used in tests and offline runs."""

    canned_reply: str = (
        "Title: Нейтральная заметка\n"
        "Tags: тест, новости\n"
        "Summary: Заглушка для оффлайн-режима."
    )

    async def complete(self, prompt: str, *, config: ModelConfig) -> str:  # pragma: no cover - trivial
        return self.canned_reply


@dataclass(slots=True)
class LLMAnnotator:
    """Prompting helper that turns raw posts into structured annotations."""

    backend: LLMBackend
    config: ModelConfig

    def build_prompt(self, text: str) -> str:
        return (
            "Ты работаешь как помощник-редактор. Дан пост из Telegram. \n"
            "1) Сформируй короткий заголовок (до 12 слов). \n"
            "2) Подбери 3-6 тегов через запятую. \n"
            "3) Дай краткий вывод (1-2 предложения). \n"
            "Верни ответ в формате:\n"
            "Title: ...\nTags: tag1, tag2\nSummary: ...\n\n"
            f"Текст: {text.strip()}"
        )

    async def annotate(self, text: str) -> dict[str, str]:
        prompt = self.build_prompt(text)
        completion = await self.backend.complete(prompt, config=self.config)
        lines = [line.strip() for line in completion.splitlines() if line.strip()]
        parsed: dict[str, str] = {}
        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            parsed[key.lower()] = value.strip()
        return {
            "title": parsed.get("title", ""),
            "tags": [tag.strip() for tag in parsed.get("tags", "").replace(",", ";").split(";") if tag.strip()],
            "summary": parsed.get("summary", ""),
        }
