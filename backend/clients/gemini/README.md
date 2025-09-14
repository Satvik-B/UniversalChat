# Gemini Client

## Overview
This client provides a modular interface for interacting with the Gemini LLM API from the backend. It is used for prompt engineering, relation extraction, and other LLM-powered tasks.

## Usage in Backend
- Import the client in your service or worker:
  ```python
  from clients.gemini.gemini_client import GeminiClient
  gemini = GeminiClient()
  gemini.extract_relations(chunk)
  ```

## Running Online (API Key Setup)
- Obtain a Gemini API key from your provider (e.g., Google AI Studio).
- Set the API key as an environment variable (e.g., `GEMINI_API_KEY`).
- Deploy your backend to your cloud provider.

## Secrets & API Key Handling
- **Never hardcode API keys.**
- Use environment variables or Secret Manager to store sensitive keys.
- Example (local):
  ```bash
  export GEMINI_API_KEY=your-key-here
  ```
- Example (GCP):
  - Store the API key in Secret Manager and grant access to your service account.

## Example Usage
```python
from clients.gemini.gemini_client import GeminiClient

gemini = GeminiClient()
relations = gemini.extract_relations("Some text chunk")
```
