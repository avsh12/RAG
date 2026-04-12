from fastapi import APIRouter

router = APIRouter(tags=["Query LLM"])


@router.post("/query")
def query():
    pass
