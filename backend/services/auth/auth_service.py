import requests
import jwt
import time
from typing import Dict, Any
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from google.cloud import firestore

from env_values import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from env_values import JWT_SECRET


JWT_ALGORITHM = "HS256"

class AuthService:
    @staticmethod
    def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for tokens with Google.
        """
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        resp = requests.post(token_url, data=data)
        if resp.status_code != 200:
            raise Exception(f"Failed to exchange code: {resp.text}")
        return resp.json()

    @staticmethod
    def verify_id_token(id_token: str) -> Dict[str, Any]:
        """
        Verify the Google ID token and extract user info.
        """
        try:
            idinfo = google_id_token.verify_oauth2_token(
                id_token, google_requests.Request(), GOOGLE_CLIENT_ID
            )
            return idinfo
        except Exception as e:
            raise Exception(f"Invalid ID token: {e}")

    @staticmethod
    def store_user_in_firestore(user_info: Dict[str, Any], tokens: Dict[str, Any]) -> None:
        """
        Store or update the user in Firestore with their tokens.
        """
        db = firestore.Client()
        user_id = user_info["sub"]
        db.collection("users").document(user_id).set({
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "tokens": tokens,
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)

    @staticmethod
    def issue_jwt(user_info: Dict[str, Any]) -> str:
        """
        Issue a JWT for the authenticated user.
        """
        payload = {
            "sub": user_info["sub"],
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "exp": int(time.time()) + 3600  # 1 hour expiry
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def extract_user_from_jwt(token: str) -> Dict[str, Any]:
        """
        Extract user info from a JWT.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("JWT expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid JWT")
