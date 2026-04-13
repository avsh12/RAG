from fastapi import Request


def get_rag_engine(request: Request):
    return request.app.state.rag
