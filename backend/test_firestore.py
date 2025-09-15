#!/usr/bin/env python3
"""
Simple test script to verify Firestore connection
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables:")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
print(f"File exists: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))}")

try:
    from clients.firestore.firestore_client import FirestoreClient
    print("\nTesting Firestore client...")
    db = FirestoreClient()
    print("✅ Firestore client initialized successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
