import logging
import sqlite3
from hashlib import sha256
from typing import Annotated

from api.utils.database import get_db
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

router = FastAPI(tags=["Authentication"])


class User(BaseModel):
    client_id: str
    email: str


def authenticate_api(
    api_key: Annotated[str, Header()],
    db_conn: Annotated[sqlite3.Connection, Depends(get_db)],
):
    hashed_api_key = sha256(api_key.encode()).hexdigest()
    cursor = db_conn.cursor()

    api_query = """select id, email from client_record where hashed_api_key = ?;"""

    cursor.execute(api_query, (hashed_api_key,))
    client_details = cursor.fetchone()

    if not client_details:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return User(client_id=client_details[0], email=client_details[1])


@router.get("/verify-key")
async def verify(
    user: Annotated[User, Depends(authenticate_api)],
):
    return {"status": "Credentials are valid!", "email": user.email}
