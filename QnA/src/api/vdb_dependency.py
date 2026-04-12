from fastapi import Request
from qdrant_client import QdrantClient


def get_qdrant_client(request: Request) -> QdrantClient:
    return request.app.state.qdrant_client
