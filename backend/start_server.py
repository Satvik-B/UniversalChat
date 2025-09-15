#!/usr/bin/env python3
"""
Startup script for the FastAPI server
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the credentials path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/satvikb/Work/UniversalChat/backend/credentials/service-account.json'

# Add current directory to Python path
sys.path.append('.')

try:
    from main import app
    print("✅ FastAPI app loaded successfully")
    print("Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    
    # Start the server
    import uvicorn
    print("\n🚀 Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure you have installed all required packages:")
    print("pip3 install fastapi uvicorn python-dotenv google-cloud-firestore google-api-python-client google-auth google-auth-oauthlib pyjwt")
