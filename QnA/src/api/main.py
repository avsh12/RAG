# import logging
from contextlib import asynccontextmanager

from api.db import create_client_record_db
from api.routers import auth, file_upload, generate_api_key, llm_query
from fastapi import FastAPI
from qdrant_client import QdrantClient
from rag.clients.embedding import EmbeddingClient
from rag.clients.llm import LLMClient
from rag.pipeline.pipeline import RAG
from rag.utils.config import settings

# logging.basicConfig(level=logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_client_record_db(settings.SQL_AUTH_DB_PATH)

    embedding_client = EmbeddingClient(path=settings.EMBEDDING_MODEL_PATH)
    vector_db_client = QdrantClient(path=settings.VECTOR_DB_PATH)
    llm_client = LLMClient(path=settings.LLM_MODEL_PATH)

    rag = RAG(vector_db_client, embedding_client, llm_client, settings.COLLECTION_NAME)
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
