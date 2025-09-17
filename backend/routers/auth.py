from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services.auth.auth_service import AuthService
from env_values import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI

router = APIRouter()
security = HTTPBearer()

@router.get("/auth/login")
def login():
    """
    Redirect the user to Google's OAuth 2.0 authorization endpoint.
    """
    drive_scope = "https://www.googleapis.com/auth/drive.readonly"

    google_oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        # --- MODIFIED LINE ---
        f"scope=openid%20email%20profile%20{drive_scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return RedirectResponse(google_oauth_url)

@router.get("/auth/callback")
def callback(request: Request, response: Response, code: Optional[str] = None):
    """
    Handle the OAuth callback from Google.
    Exchange the code for tokens, verify the ID token, store user info and tokens in Firestore, and issue a JWT.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")
    try:
        tokens = AuthService.exchange_code_for_tokens(code)
        idinfo = AuthService.verify_id_token(tokens["id_token"])
        AuthService.store_user_in_firestore(idinfo, tokens)
        jwt_token = AuthService.issue_jwt(idinfo)
        # Return JWT in response (could also set as cookie)
        return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Return the current authenticated user's info from JWT.
    """
    token = credentials.credentials
    try:
        user = AuthService.extract_user_from_jwt(token)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
