# Firestore Client

## Overview
This client provides a modular interface for interacting with Google Firestore from the backend. It handles user data, ingestion status, and other persistent storage needs.

## Usage in Backend
- Import the client in your service or worker:
  ```python
  from clients.firestore.firestore_client import FirestoreClient
  db = FirestoreClient()
  db.get_user_token(user_id)
  db.update_status(doc_id, status, error)
  ```

## Running Online (GCP Setup)
- Enable Firestore in your Google Cloud project.
- Deploy your backend to GCP (Cloud Run, Cloud Functions, etc.).
- Grant the service account the `roles/datastore.user` permission.
- Locally, authenticate with `gcloud auth application-default login` or set the `GOOGLE_APPLICATION_CREDENTIALS` env var to your service account key.

## Secrets & API Key Handling
- **Never hardcode credentials.**
- Use environment variables or Google Secret Manager to store sensitive keys.
- Example (local):
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  ```
- Example (GCP):
  - Store secrets in Secret Manager and grant access to your service account.

## Example Usage
```python
from clients.firestore.firestore_client import FirestoreClient

db = FirestoreClient()
token = db.get_user_token("user123")
db.update_status("doc456", "success")
```
