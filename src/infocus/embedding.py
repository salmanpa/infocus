from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .config import ModelConfig


class EmbeddingBackend(Protocol):
    async def embed(self, texts: Sequence[str], *, config: ModelConfig) -> list[list[float]]:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class LocalEmbedder:
    """Async client for a local embedding service compatible with `nomic-embed`.

    The service can be launched with GPU support and handles batching
    internally. For small payloads we send the full text list in a single
    request.
    """

    base_url: str = "http://localhost:11434"

    async def embed(self, texts: Sequence[str], *, config: ModelConfig) -> list[list[float]]:
        import httpx  # Imported lazily to avoid mandatory dependency during tests.

        payload = {"model": config.embedding_model, "input": list(texts)}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.post("/api/embed", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])


@dataclass(slots=True)
class StubEmbedder:
    """Deterministic embedder for tests and offline mode."""

    async def embed(self, texts: Sequence[str], *, config: ModelConfig) -> list[list[float]]:  # pragma: no cover - trivial
        return [[float(len(text))] for text in texts]
