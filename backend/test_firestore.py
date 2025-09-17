#!/usr/bin/env python3
"""
Simple test script to verify Firestore connection
"""
from env_values import GOOGLE_APPLICATION_CREDENTIALS

print("Environment variables:")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {GOOGLE_APPLICATION_CREDENTIALS}")
print(f"File exists: {os.path.exists(GOOGLE_APPLICATION_CREDENTIALS)}")

try:
    from clients.firestore.firestore_client import FirestoreClient
    print("\nTesting Firestore client...")
    db = FirestoreClient()
    print("✅ Firestore client initialized successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
