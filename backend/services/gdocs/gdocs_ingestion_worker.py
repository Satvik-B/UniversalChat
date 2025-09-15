from services.ingestion.base import BaseIngestionWorker
from typing import List, Dict, Any
from clients.firestore.firestore_client import FirestoreClient
from clients.gemini.gemini_client import GeminiClient
from clients.mem0.mem0_client import Mem0Client
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GDocsIngestionWorker(BaseIngestionWorker):
    """
    Ingestion worker for Google Docs. Implements source-specific logic for fetching, chunking, extracting, and storing content and relations.
    Follows SOLID principles for extensibility and maintainability.
    """
    def __init__(self, gdocs_mem0_client: Mem0Client, relations_mem0_client: Mem0Client, firestore_client: FirestoreClient, gemini_client: GeminiClient):
        self.gdocs_mem0_client = gdocs_mem0_client
        self.relations_mem0_client = relations_mem0_client
        self.firestore_client = firestore_client
        self.gemini_client = gemini_client

    def fetch_document_content(self, doc_id: str, user_id: str) -> str:
        """
        Fetch the raw text of a Google Doc using the user's credentials.
        Uses FirestoreClient to get the user's access token, then Google Docs API to fetch content.
        """
        access_token = self.firestore_client.get_user_token(user_id)
        if not access_token:
            raise Exception(f"No access token found for user {user_id}")
        creds = Credentials(token=access_token)
        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id).execute()
        print(doc)
        return self._extract_text_from_document(doc)

    def _extract_text_from_document(self, doc: dict) -> str:
        """
        Extract plain text from the Google Docs API document structure.
        """
        text = []
        for element in doc.get("body", {}).get("content", []):
            paragraph = element.get("paragraph")
            if not paragraph:
                continue
            for elem in paragraph.get("elements", []):
                txt = elem.get("textRun", {}).get("content")
                if txt:
                    text.append(txt)
        return "".join(text)

    def extract_relations_with_gemini(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Call the Gemini API to extract entities and relationships from each chunk.
        Uses GeminiClient.
        """
        relations = []
        for chunk in chunks:
            rel = self.gemini_client.extract_relations(chunk)
            relations.extend(rel)
        return relations

    def store_content_in_mem0(self, chunks: List[str], doc_id: str) -> None:
        """
        Store the content chunks in the Google Docs Mem0 content memory instance.
        Uses Mem0Client.
        """
        self.gdocs_mem0_client.store_chunks(doc_id, chunks)

    def store_relations_in_mem0(self, relations: List[Dict[str, Any]], doc_id: str) -> None:
        """
        Store the extracted relations in the central Mem0 relations memory instance.
        Uses Mem0Client.
        """
        self.relations_mem0_client.store_relations(doc_id, relations)

    def update_ingestion_status(self, doc_id: str, status: str, error: str = None) -> None:
        """
        Update the ingestion status and error details in Firestore for observability.
        Uses FirestoreClient.
        """
        self.firestore_client.update_status(doc_id, status, error)
