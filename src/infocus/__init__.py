"""Core pipeline for local LLM-based news annotation."""

from .config import ModelConfig
from .llm import LLMAnnotator, OllamaBackend, StubBackend
from .embedding import EmbeddingBackend, LocalEmbedder, StubEmbedder
from .pipeline import AnnotationPipeline, AnnotatedPost

__all__ = [
    "ModelConfig",
    "LLMAnnotator",
    "OllamaBackend",
    "StubBackend",
    "EmbeddingBackend",
    "LocalEmbedder",
    "StubEmbedder",
    "AnnotationPipeline",
    "AnnotatedPost",
]
