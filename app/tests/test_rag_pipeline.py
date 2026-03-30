from app.rag_pipeline import RagPipeline


def test_rag_pipeline_retrieves_docs() -> None:
    pipeline = RagPipeline()
    response = pipeline.ask("What are AI release requirements?")

    assert "answer" in response
    assert len(response["retrieved_documents"]) >= 1
    assert "policy" in response["answer"].lower()


def test_retrieval_top_k_override() -> None:
    pipeline = RagPipeline()
    docs = pipeline.retrieve("How long are records retained?", top_k=3)
    assert len(docs) == 3
