import asyncio

from infocus import (
    AnnotationPipeline,
    LLMAnnotator,
    ModelConfig,
    StubBackend,
    StubEmbedder,
)


def test_annotation_pipeline_stubbed():
    config = ModelConfig()
    annotator = LLMAnnotator(backend=StubBackend(), config=config)
    embedder = StubEmbedder()
    pipeline = AnnotationPipeline(annotator=annotator, embedder=embedder, config=config)

    posts = ["Короткая новость про запуск сервиса."]

    results = asyncio.run(pipeline.annotate_posts(posts))
    assert len(results) == 1
    item = results[0]
    assert item.title.startswith("Нейтральная")
    assert item.tags == ["тест", "новости"]
    assert item.embedding == [float(len(posts[0]))]
