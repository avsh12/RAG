from typing import Annotated

from api.routers.auth import User, authenticate_api
from api.utils.util import get_rag_engine
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from rag.pipeline.pipeline import RAG

router = APIRouter(tags=["Query LLM"])


class QueryPayload(BaseModel):
    text: str


@router.post("/query")
def query(
    user: Annotated[User, Depends(authenticate_api)],
    rag: Annotated[RAG, Depends(get_rag_engine)],
    text: Annotated[str, Body()],
):
    response = rag.query(user.client_id, text)

    return {"content": response["content"], "context": response["context"]}
