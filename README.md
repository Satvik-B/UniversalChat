# UniversalChat

## Project Overview

UniversalChat is an intelligent personal knowledge assistant that connects to your applications (starting with Google Docs), ingests your data, and builds a sophisticated, multi-instance Mem0 memory architecture. It separates application-specific content from a central knowledge graph of cross-source relationships, enabling synthesized, context-rich answers to your questions via a chat interface.

## Architecture Summary

- **Frontend:** React (Next.js) SPA for chat and user management
- **Backend:** FastAPI microservices for API, authentication, LLM orchestration, and ingestion
- **Data Layer:** Firestore (primary DB), multiple Mem0 instances (content and relations memory)
- **Cloud:** Google Cloud Platform (Cloud Run, Cloud Functions, Secret Manager)

See `/docs/architecture.md` for detailed diagrams, including the Low Level Design (LLD) for authentication. All major features require LLD review and confirmation before implementation.

## Technology Stack

- **Frontend:** React, Next.js, MaterialUI, TypeScript
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, mem0-python, Google Cloud Firestore
- **Testing:** pytest (backend), Jest & React Testing Library (frontend)
- **Deployment:** Google Cloud Run, Cloud Functions, GitHub Actions CI/CD

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud account (for deployment)

### Backend Setup
```bash
cd backend
# Install dependencies
poetry install
# Run development server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Setup Instructions

### 1. Install Poetry (Python dependency manager)
If you don't have Poetry installed:
```bash
pip install poetry
```

### 2. Install Backend Dependencies
From the `backend` directory:
```bash
cd backend
poetry install
```
# Set Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/Users/satvikb/Work/UniversalChat/backend/credentials/service-account.json"

# Create and configure .env file
cp env.example .env
# Edit .env with your actual API keys and credentials
```

### 3. Run Backend Tests
From the `backend` directory:
```bash
PYTHONPATH=. python3 -m pytest
```

### 4. Frontend Setup
From the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```

---

For architecture diagrams, ADRs, and further documentation, see the `/docs` folder.

## Deployment Guide

1. **Google Cloud Setup:**
   - Create a GCP project, enable Firestore, Cloud Run, Cloud Functions, and Secret Manager.
   - Store all secrets (API keys, OAuth credentials) in Secret Manager.
2. **Backend Deployment:**
   - Build and deploy Docker images to Cloud Run.
   - Deploy ingestion worker as a Cloud Function.
3. **Frontend Deployment:**
   - Deploy to Vercel or Cloud Run.
4. **CI/CD:**
   - Set up GitHub Actions to run tests and deploy on main branch merges.

See `/docs/deployment.md` for detailed steps and environment variable documentation.
