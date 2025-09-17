from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
from services.gdocs.gdocs_ingestion_worker import GDocsIngestionWorker
# Assume these are initialized elsewhere and imported here
from clients.firestore.firestore_client import FirestoreClient
from clients.gemini.gemini_client import GeminiClient
from clients.mem0.mem0_client import Mem0Client
from env_values import MEM0_GDOCS_INSTANCE_URL, MEM0_GDOCS_API_KEY, MEM0_RELATIONS_INSTANCE_URL, MEM0_RELATIONS_API_KEY

router = APIRouter()

# Example: Dependency injection or global setup

firestore_client = FirestoreClient()
gdocs_mem0_client = Mem0Client(
    instance_url=MEM0_GDOCS_INSTANCE_URL, 
    api_key=MEM0_GDOCS_API_KEY
)
relations_mem0_client = Mem0Client(
    instance_url=MEM0_RELATIONS_INSTANCE_URL, 
    api_key=MEM0_RELATIONS_API_KEY
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

class IngestAllRequest(BaseModel):
    user_id: str

class ListDocsRequest(BaseModel):
    user_id: str

class ListDocsResponse(BaseModel):
    doc_ids: List[str]

def process_doc_text(doc_text: str, title: str, doc_id: str) -> tuple[list[str], list[Dict[str, Any]]]:
    # Placeholder for processing logic
    print(f"Processing document ID: {doc_id} with title: {title}")  # Debug print

    print(f"creating chunks for doc_id: {doc_id}")  # Debug print
    chunks = ingestion_worker.chunk_document(doc_text)
    print(f"created {len(chunks)} chunks for doc_id: {doc_id}")  # Debug print

    print(f"extracting relations for doc_id: {doc_id}")  # Debug print
    relations = ingestion_worker.extract_relations_with_gemini(chunks, title, doc_id)
    # ingestion_worker.store_content_in_mem0(chunks, doc_id)
    # ingestion_worker.store_relations_in_mem0(relations, doc_id)
    return chunks, relations

@router.post("/ingest/gdocs")
def ingest_gdocs(request: IngestRequest) -> Any:
    """
    Trigger the Google Docs ingestion pipeline for a given doc_id and user_id.
    Runs fetch, chunk, extract, store, and update status steps.
    """
    try:
        # 1. Fetch document content
        doc_text, title = ingestion_worker.fetch_document_content(request.doc_id, request.user_id)
        # 2. Process document text (chunking, relation extraction, storing)
        processed = process_doc_text(doc_text, title=title, doc_id=request.doc_id)
        # 5. Update status
        ingestion_worker.update_ingestion_status(request.doc_id, "success")
        return {"status": "ok", "chunks": len(processed[0]), "relations": len(processed[1])}
    except Exception as e:
        ingestion_worker.update_ingestion_status(request.doc_id, "error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

@router.post("/ingest/gdocs/list")
def list_user_docs(request: ListDocsRequest) -> ListDocsResponse:
    """
    List all document IDs for a given user.
    """
    try:
        # Use Google Drive API to list user's Google Docs
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        creds = firestore_client.get_user_credentials(request.user_id)
        if not creds:
            raise HTTPException(status_code=404, detail=f"No credentials found for user {request.user_id}")
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
    
@router.post("/ingest/gdocs/all")
def ingest_all_gdocs(request: IngestAllRequest) -> Any:
    """
    Trigger ingestion for all Google Docs across all users.
    This is a placeholder and should be implemented with proper user iteration and rate limiting.
    """
    try:
        # Use Google Drive API to list user's Google Docs
        from googleapiclient.discovery import build
        
        creds = firestore_client.get_user_credentials(request.user_id)
        if not creds:
            raise HTTPException(status_code=404, detail=f"No credentials found for user {request.user_id}")
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Query for Google Docs files
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            fields="files(id, name)"
        ).execute()
        
        doc_ids = [file['id'] for file in results.get('files', [])]

        for doc_id in doc_ids:
            doc_text, title = ingestion_worker.fetch_document_content(doc_id, request.user_id)
            process_doc_text(doc_text, title=title, doc_id=doc_id)
            ingestion_worker.update_ingestion_status(doc_id, "success")
            # Further steps would go here...

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest all docs: {e}")
