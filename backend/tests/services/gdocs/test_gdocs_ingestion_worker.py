import pytest
from unittest.mock import MagicMock
from services.gdocs.gdocs_ingestion_worker import GDocsIngestionWorker

@pytest.fixture
def worker():
    gdocs_mem0_client = MagicMock()
    relations_mem0_client = MagicMock()
    gdocs_api_client = MagicMock()
    gemini_api_client = MagicMock()
    firestore_client = MagicMock()
    return GDocsIngestionWorker(
        gdocs_mem0_client,
        relations_mem0_client,
        gdocs_api_client,
        gemini_api_client,
        firestore_client
    )

def test_fetch_document_content(worker):
    # Should return mock content
    content = worker.fetch_document_content("doc123", "user456")
    assert "doc_id doc123" in content
    assert "user_id user456" in content

def test_extract_relations_with_gemini(worker):
    chunks = ["chunk1", "chunk2"]
    relations = worker.extract_relations_with_gemini(chunks)
    assert len(relations) == 2
    assert relations[0]["chunk"] == "chunk1"
    assert "mock_relation" in relations[0]["relations"]

def test_store_content_in_mem0(worker):
    # Should not raise and should be callable
    worker.store_content_in_mem0(["chunk1"], "doc123")

def test_store_relations_in_mem0(worker):
    # Should not raise and should be callable
    worker.store_relations_in_mem0([{"chunk": "c", "relations": []}], "doc123")

def test_update_ingestion_status(worker):
    # Should not raise and should be callable
    worker.update_ingestion_status("doc123", "success")

def test_full_ingestion_flow(worker):
    # Simulate a full flow with all mocks
    doc_id = "doc123"
    user_id = "user456"
    content = worker.fetch_document_content(doc_id, user_id)
    chunks = worker.chunk_document(content)
    relations = worker.extract_relations_with_gemini(chunks)
    worker.store_content_in_mem0(chunks, doc_id)
    worker.store_relations_in_mem0(relations, doc_id)
    worker.update_ingestion_status(doc_id, "success")
