# main.py
# FastAPI app entrypoint

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from routers import health, auth, gdocs_ingest

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(gdocs_ingest.router)
