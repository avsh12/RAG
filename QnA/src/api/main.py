import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, status
from pandas import read_parquet
from pydantic import BaseModel
from qdrant_client import QdrantClient
from rag.pipeline.infer import fetch_context

from .db import create_client_record_db
from .routers import auth, file_upload, generate_api_key

logging.basicConfig(level=logging.ERROR)


class Query(BaseModel):
    query: list[str]


class User(BaseModel):
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    filepath = "data/auth/client_record.db"
    create_client_record_db(filepath)
    yield


app = FastAPI(lifespan=lifespan)

# API generation phase
app.include_router(generate_api_key.router)
# API validation phase
app.include_router(auth.router)
# File upload phase
app.include_router(file_upload.router)
# Query phase


@app.get("/")
async def root():
    return {"message": "Welocome to the RAG QnA!"}


@app.post("/context/")
async def context(query: Query):
    collection_name = "cat_facts"
    filepath = "data/"

    emb_url = "http://localhost:8181/embedding"

    client = QdrantClient(path=filepath)
    db = read_parquet(os.path.join(filepath, "cat_facts.parquet"))

    responses = fetch_context(query.query, db, client, collection_name, emb_url)

    return responses
