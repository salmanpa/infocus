from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .config import ModelConfig
from .embedding import EmbeddingBackend
from .llm import LLMAnnotator


@dataclass(slots=True)
class AnnotatedPost:
    text: str
    title: str
    tags: list[str]
    summary: str
    embedding: list[float]


@dataclass(slots=True)
class AnnotationPipeline:
    """End-to-end annotation pipeline combining LLM and embedding backends."""

    annotator: LLMAnnotator
    embedder: EmbeddingBackend
    config: ModelConfig

    async def annotate_posts(self, posts: Sequence[str]) -> list[AnnotatedPost]:
        annotated: list[AnnotatedPost] = []
        for post in posts:
            llm_result = await self.annotator.annotate(post)
            embeddings = await self.embedder.embed([post], config=self.config)
            vector = embeddings[0] if embeddings else []
            annotated.append(
                AnnotatedPost(
                    text=post,
                    title=llm_result["title"],
                    tags=llm_result["tags"],
                    summary=llm_result["summary"],
                    embedding=vector,
                )
            )
        return annotated
