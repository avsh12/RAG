import hashlib
import logging
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

router = APIRouter(tags=["Authentication"])


def authentication(email: str, heashed_api_key: str, filepath: str):
    try:
        with sqlite3.connect(filepath) as connection:
            cursor = connection.cursor()

            read_query = (
                """select 1 from client_record where (email=?) & (hashed_api_key=?);"""
            )
            cursor.execute(read_query, (email, heashed_api_key))
            status = cursor.fetchone() is not None

            return status
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error in {filepath}: {e}")
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in {filepath}: {e}")
        raise


@router.get("/verify-key")
async def verify(email: Annotated[str, Header()], api_key: Annotated[str, Header()]):
    hashed_api_key = hashlib.sha256(api_key.encode()).hexdigest()

    filepath = "data/auth/client_record.db"

    status = authentication(email, hashed_api_key, filepath)

    return {
        "status": "Credentials are valid!" if status else "Credentials are invalid!"
    }
