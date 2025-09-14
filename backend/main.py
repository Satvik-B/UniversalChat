# main.py
# FastAPI app entrypoint

from fastapi import FastAPI
from routers import health, auth

app = FastAPI()
app.include_router(health.router)
app.include_router(auth.router)
