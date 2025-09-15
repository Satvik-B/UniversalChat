import os
from typing import Any, Optional
from google.cloud import firestore
from google.api_core.exceptions import NotFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirestoreClient:
    """
    Client for interacting with Google Firestore for user data, ingestion status, and other persistent storage needs.
    Loads credentials securely from environment or GCP default.
    """
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Firestore client. Loads credentials from env var or uses default.
        """
        creds_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if creds_path and os.path.exists(creds_path):
            self.db = firestore.Client.from_service_account_json(creds_path)
        else:
            try:
                self.db = firestore.Client()  # Uses default credentials (GCP or local auth)
            except Exception as e:
                raise Exception(f"Failed to initialize Firestore client. Please set GOOGLE_APPLICATION_CREDENTIALS or authenticate with gcloud. Error: {e}")

    def get_user_token(self, user_id: str) -> Optional[str]:
        """
        Fetch the user's Google OAuth access token from Firestore.
        """
        try:
            doc = self.db.collection("users").document(user_id).get()
            if doc.exists:
                tokens = doc.to_dict().get("tokens", {})
                return tokens.get("access_token")
            return None
        except NotFound:
            return None
        except Exception as e:
            # TODO: Add logging
            return None

    def update_status(self, doc_id: str, status: str, error: str = None) -> None:
        """
        Update the ingestion status and error details for a document in Firestore.
        """
        try:
            data = {"status": status}
            if error:
                data["error"] = error
            self.db.collection("ingestion_status").document(doc_id).set(data, merge=True)
        except Exception as e:
            # TODO: Add logging
            pass

    def get(self, collection: str, doc_id: str) -> Optional[Any]:
        """
        Generic get for any collection/document.
        """
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            # TODO: Add logging
            return None

    def set(self, collection: str, doc_id: str, data: dict) -> None:
        """
        Generic set for any collection/document.
        """
        try:
            self.db.collection(collection).document(doc_id).set(data, merge=True)
        except Exception as e:
            # TODO: Add logging
            pass
