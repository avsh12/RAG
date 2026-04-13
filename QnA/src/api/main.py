import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import date, timedelta

from api.config.config import SQL_AUTH_PATH
from api.db import create_client_record_db
from api.routers import auth, file_upload, generate_api_key, llm_query
from fastapi import FastAPI, HTTPException, status
from pandas import read_parquet
from pydantic import BaseModel
from qdrant_client import QdrantClient
from rag.clients.embedding import EmbeddingClient
from rag.clients.llm import LLMClient
from rag.pipeline.infer import fetch_context
from rag.pipeline.pipeline import RAG
from rag.utils.config import settings

logging.basicConfig(level=logging.ERROR)


class Query(BaseModel):
    query: list[str]


class User(BaseModel):
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth_db_path = "data/user/auth/client_record.db"
    vector_db_path = "data/collection"
    embed_model_path = "http://localhost:8181/embedding"
    llm_model_path = "http://localhost:8080/v1/chat/completions"
    collection_name = "cat_facts"
    print(f"SQL_AUTH_DB_PATH: {settings.SQL_AUTH_DB_PATH}")
    create_client_record_db(settings.SQL_AUTH_DB_PATH)

    embedding_client = EmbeddingClient(path=embed_model_path)
    vector_db_client = QdrantClient(path=vector_db_path)
    llm_client = LLMClient(path=llm_model_path)

    rag = RAG(vector_db_client, embedding_client, llm_client, collection_name)
    app.state.rag = rag
    yield
    rag.embedding_client.close()
    rag.qdrant_client.close()
    rag.llm_client.close()


app = FastAPI(lifespan=lifespan)

# API generation phase
app.include_router(generate_api_key.router)
# API validation phase
app.include_router(auth.router)
# File upload phase
app.include_router(file_upload.router)
# Query phase
app.include_router(llm_query.router)


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
