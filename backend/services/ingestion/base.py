import abc
from typing import List, Dict, Any

class BaseIngestionWorker(abc.ABC):
    """
    Abstract base class for all ingestion workers. Defines the skeleton for ingestion logic.
    """
    @abc.abstractmethod
    def fetch_document_content(self, doc_id: str, user_id: str) -> str:
        """
        Fetch the raw text/content for a document from the source application.
        """
        pass

    def chunk_document(self, doc_text: str) -> List[str]:
        """
        Default implementation: Split document text into chunks (e.g., paragraphs).
        Subclasses may override for custom chunking logic.
        """
        return [doc_text[i:i+1000] for i in range(0, len(doc_text), 1000)]  # Simple fixed-size chunking

    @abc.abstractmethod
    def extract_relations_with_gemini(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Extract entities and relationships from each chunk using Gemini API.
        """
        pass

    @abc.abstractmethod
    def store_content_in_mem0(self, chunks: List[str], doc_id: str) -> None:
        """
        Store content chunks in the application-specific Mem0 instance.
        """
        pass

    @abc.abstractmethod
    def store_relations_in_mem0(self, relations: List[Dict[str, Any]], doc_id: str) -> None:
        """
        Store extracted relations in the central relations Mem0 instance.
        """
        pass

    @abc.abstractmethod
    def update_ingestion_status(self, doc_id: str, status: str, error: str = None) -> None:
        """
        Update the ingestion status and error details in Firestore for observability.
        """
        pass
