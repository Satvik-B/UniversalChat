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

    def fetch_document_content(self, doc_id: str, user_id: str) -> tuple[str, str]:
        """
        Fetch the raw text of a Google Doc using the user's credentials.
        Uses FirestoreClient to get the user's access token, then Google Docs API to fetch content.
        """
        creds = self.firestore_client.get_user_credentials(user_id)
        if not creds:
            raise Exception(f"No credentials found for user {user_id}")

        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id).execute()
        return self._extract_text_from_document(doc), doc.get("title", "Untitled Document")

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

    def extract_relations_with_gemini(self, chunks: List[str], doc_title: str, doc_id: str) -> List[Dict[str, Any]]:
        """
        Call the Gemini API to extract entities and relationships from each chunk.
        Uses GeminiClient.
        """
        print(f"Extracting relations for doc_id: {doc_id} with title: {doc_title}")  # Debug print
        relations = []
        for chunk in chunks:
            prompt = self._create_relations_prompt(doc_text=chunk, doc_title=doc_title, doc_id=doc_id)
            print(f"Prompt sent to Gemini for doc_id {doc_id}: {prompt[:500]}")
            rel = self.gemini_client.call_llm(prompt)
            print("Gemini response:", rel)  # Debug print
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

    def _create_relations_prompt(self, doc_text: str, doc_title: str, doc_id: str) -> str:
        """
        Create a prompt for the Gemini API to extract relations from the given text.
        """
        return f"# ROLE & GOAL \
                    You are an expert Knowledge Graph extraction system. Your goal is to read the provided document context (ID, title, and body) and identify all key entities and their relationships. You must structure these relationships as a list of JSON objects, each representing a (Subject, Relation, Object) triplet. \
                    \
                    # SCHEMA DEFINITION \
                    You MUST strictly adhere to the following entity and relation types. Do not create new types.\
                    \
                    ## Entity Types:\
                    - Document: The document itself.\
                    - Person: An individual\'s name (e.g., \"Alice Smith\").\
                    - Project: A named project or initiative (e.g., \"Project Phoenix\"). \
                    - Team: A named group or department (e.g., \"Marketing Team\").\
                    - Organization: A company or institution (e.g., \"Acme Corp\").\
                    - Date: A specific date or deadline (e.g., \"September 17, 2025\").\
                    - Task: A specific action item or deliverable.\
                    - Concept: An important abstract idea or topic mentioned (e.g., \"user engagement\").\
                    \
                    ## Relation Types:\
                    - HAS_TITLE: Connects the document ID to its title.\
                    - CONTAINS_CONTENT: Connects the document to a key entity mentioned within it.\
                    - MENTIONS: A subject entity refers to an object entity.\
                    - ASSIGNED_TO: A task is assigned to a Person or Team.\
                    - DUE_ON: A project or task has a specific deadline.\
                    - PART_OF: An entity is a component of a larger project or team.\
                    - REPORTS_TO: A person reports to another person.\
                    - WORKS_ON: A person or team works on a project.\
                    \
                    # OUTPUT FORMAT\
                    - The output MUST be a valid JSON array `[]`.\
                    - Each element in the array is a JSON object representing a single relation.\
                    - Each object must have three keys: \"subject\", \"relation\", and \"object\".\
                    - The document itself should be identified by its ID.\
                    \
                    # DOCUMENT CONTEXT\
                    - Document ID: \"{doc_id}\"\
                    - Document Title: \"{doc_title}\"\
                    - Document Body: \
                    \"\"\"\
                    {doc_text}\
                    \"\"\"\
                    \
                    # EXTRACTED RELATIONS (JSON OUTPUT ONLY):\
                    ```json\
                    [\
                    // expecting your JSON output here\
                    ]\
            "
