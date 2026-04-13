from typing import Annotated

from api.routers.auth import User, authenticate_api
from api.utils.util import get_rag_engine
from fastapi import APIRouter, Depends
from rag.pipeline.pipeline import RAG

router = APIRouter(tags=["Query LLM"])


@router.post("/query")
def query(
    user: Annotated[User, Depends(authenticate_api)],
    rag: Annotated[RAG, Depends(get_rag_engine)],
    text: str,
):
    response = rag.query(user.client_id, text)

    return {"response": response["content"], "context": response["context"]}
