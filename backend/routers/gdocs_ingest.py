from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List
from services.gdocs.gdocs_ingestion_worker import GDocsIngestionWorker
# Assume these are initialized elsewhere and imported here
from clients.firestore.firestore_client import FirestoreClient
from clients.gemini.gemini_client import GeminiClient
from clients.mem0.mem0_client import Mem0Client

router = APIRouter()

# Example: Dependency injection or global setup
import os
firestore_client = FirestoreClient()
gdocs_mem0_client = Mem0Client(
    instance_url=os.getenv("MEM0_GDOCS_INSTANCE_URL", "https://mem0-gdocs.example.com"), 
    api_key=os.getenv("MEM0_GDOCS_API_KEY", "gdocs-key")
)
relations_mem0_client = Mem0Client(
    instance_url=os.getenv("MEM0_RELATIONS_INSTANCE_URL", "https://mem0-relations.example.com"), 
    api_key=os.getenv("MEM0_RELATIONS_API_KEY", "relations-key")
)
gemini_client = GeminiClient()
ingestion_worker = GDocsIngestionWorker(
    gdocs_mem0_client=gdocs_mem0_client,
    relations_mem0_client=relations_mem0_client,
    firestore_client=firestore_client,
    gemini_client=gemini_client
)

class IngestRequest(BaseModel):
    doc_id: str
    user_id: str

class ListDocsRequest(BaseModel):
    user_id: str

class ListDocsResponse(BaseModel):
    doc_ids: List[str]

@router.post("/ingest/gdocs")
def ingest_gdocs(request: IngestRequest) -> Any:
    """
    Trigger the Google Docs ingestion pipeline for a given doc_id and user_id.
    Runs fetch, chunk, extract, store, and update status steps.
    """
    try:
        # 1. Fetch document content
        doc_text = ingestion_worker.fetch_document_content(request.doc_id, request.user_id)
        print(doc_text)
        # 2. Chunk document
        # chunks = ingestion_worker.chunk_document(doc_text)
        # 3. Extract relations
        # relations = ingestion_worker.extract_relations_with_gemini(chunks)
        # 4. Store content and relations
        # ingestion_worker.store_content_in_mem0(chunks, request.doc_id)
        # ingestion_worker.store_relations_in_mem0(relations, request.doc_id)
        # 5. Update status
        ingestion_worker.update_ingestion_status(request.doc_id, "success")
        return {"status": "ok", "chunks": 0, "relations": 0}
    except Exception as e:
        ingestion_worker.update_ingestion_status(request.doc_id, "error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

@router.post("/ingest/gdocs/list")
def list_user_docs(request: ListDocsRequest) -> ListDocsResponse:
    """
    List all document IDs for a given user.
    """
    try:
        # Get user's access token to query Google Drive API for their documents
        access_token = firestore_client.get_user_token(request.user_id)
        if not access_token:
            raise HTTPException(status_code=404, detail=f"No access token found for user {request.user_id}")
        
        # Use Google Drive API to list user's Google Docs
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        creds = Credentials(token=access_token)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Query for Google Docs files
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            fields="files(id, name)"
        ).execute()
        
        doc_ids = [file['id'] for file in results.get('files', [])]
        return ListDocsResponse(doc_ids=doc_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list docs: {e}")
