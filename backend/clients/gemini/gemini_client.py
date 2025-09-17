
import requests
from typing import Any, Dict, List, Optional
from env_values import GEMINI_API_KEY
from env_values import GEMINI_API_URL
import json

class GeminiClient:
    """
    Client for interacting with the Gemini LLM API for relation extraction and other LLM-powered tasks.
    Loads API key securely from environment or Secret Manager.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client. Loads API key from env var if not provided.
        """
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set in environment or provided to GeminiClient.")
        # TODO: Optionally load from Secret Manager if running on GCP
        self.base_url = GEMINI_API_URL

    def call_llm(self, prompt: str, model: str = 'gemini-2.5-flash') -> Dict[str, Any]:
        """
        Make a generic call to the Gemini LLM API with the given prompt.
        """
        url = f"{GEMINI_API_URL}/{model}:generateContent"
        print("------")
        print(prompt)
        print("------")
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            # --- 3. Add generation configuration for better control ---
            "generationConfig": {
                "temperature": 0.2, # Lower temperature for deterministic tasks like extraction
                "topP": 1,
                "topK": 1,
                "maxOutputTokens": 8192,
                "response_mime_type": "application/json" # Important for JSON-only prompts
            }
        }
        try:
            # --- 4. Make the POST request ---
            print(f"Sending request to Gemini API at {url}")  # Debug print
            response = requests.post(url, json=payload, headers=headers)
            print(f"Received response: {response.status_code}")  # Debug print
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            # --- 5. Safely parse the response ---
            response_data = response.json()
            relations_json = json.loads(result['output'])
            
            print(json.dumps(relations_json, indent=2))

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the API request: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
        
        # TODO: Replace with real Gemini API endpoint and handle errors
        # Example placeholder:
        # response = requests.post(f"{self.base_url}/llm/generate", json=payload, headers=headers)
        # response.raise_for_status()
        # return response.json()
        return {"output": "mock LLM output for prompt: " + str(response_data)}

    def _build_relation_extraction_prompt(self, text: str) -> str:
        """
        Build a prompt for relation extraction from the given text.
        """
        return f"Extract all entities and relationships from the following text:\n{text}"
