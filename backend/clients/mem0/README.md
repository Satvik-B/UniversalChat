# Mem0 Client

## Overview
This client provides a modular interface for interacting with Mem0 memory instances (content and relations) from the backend. It is used to store and retrieve content chunks and cross-source relationships.

## Usage in Backend
- Import the client in your service or worker:
  ```python
  from clients.mem0.mem0_client import Mem0Client
  mem0 = Mem0Client(instance_url, api_key)
  mem0.store_chunks(doc_id, chunks)
  mem0.store_relations(doc_id, relations)
  ```

## Running Online (API Key/Setup)
- Obtain the Mem0 instance URL and API key from your Mem0 provider.
- Set the API key as an environment variable (e.g., `MEM0_API_KEY`).
- Deploy your backend to your cloud provider.

## Secrets & API Key Handling
- **Never hardcode API keys.**
- Use environment variables or Secret Manager to store sensitive keys.
- Example (local):
  ```bash
  export MEM0_API_KEY=your-key-here
  ```
- Example (GCP):
  - Store the API key in Secret Manager and grant access to your service account.

## Example Usage
```python
from clients.mem0.mem0_client import Mem0Client

mem0 = Mem0Client("https://mem0-instance-url", "api-key")
mem0.store_chunks("doc123", ["chunk1", "chunk2"])
mem0.store_relations("doc123", [{"entity": "foo"}])
```
