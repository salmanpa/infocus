from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ModelConfig:
    """Configuration for LLM and embedding models.

    Defaults are tuned for a single 16GB GPU and CPU fallbacks. The LLM is
    small enough to run with 4-bit quantization, while the embedder targets
    multilingual coverage.
    """

    llm_model: str = "qwen2.5:0.5b-instruct"
    """Model alias for Ollama or local runtime. Fits comfortably on 16GB GPU."""

    embedding_model: str = "nomic-embed-text:latest"
    """Model alias for a local embedding service (nomic-embed) with GPU support."""

    max_new_tokens: int = 256
    temperature: float = 0.3

    @classmethod
    def for_mistral(cls) -> "ModelConfig":
        """Preset that targets a 4-bit Mistral 7B deployment."""

        return cls(
            llm_model="mistral:instruct",
            max_new_tokens=256,
            temperature=0.4,
        )
