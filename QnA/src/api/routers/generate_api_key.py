import hashlib
import logging
import os
import secrets
import sqlite3
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from rag.utils.config import settings

router = APIRouter(tags=["API generation and Authentication"])

# NAMESPACE = uuid.UUID("73c177ef-bc8b-42d0-9762-71f13a3b3a45")

logging.basicConfig(level=logging.ERROR)


class User(BaseModel):
    email: str


def get_id(user):
    id = uuid.uuid5(settings.ID_NAMESPACE, user)
    return str(id)


def insert_into_record(id: str, user: str, key: str, filepath: str):
    try:
        with sqlite3.connect(filepath) as connection:
            cursor = connection.cursor()

            insert_query = """insert into client_record(id, email, hashed_api_key)
                            values(?, ?, ?);"""

            cursor.execute(insert_query, (id, user, key))

            connection.commit()
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error in {filepath} for user {user}: {e}")
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in {filepath}: {e}")
        raise


def get_email_from_id(id: str, filepath: str) -> str:
    try:
        with sqlite3.connect(filepath) as connection:
            cursor = connection.cursor()

            read_query = """select email from client_record where id=?;
                            """

            cursor.execute(read_query, (id,))
            email = cursor.fetchone()
            print(f"email: {email}")

            return email
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error in {filepath}: {e}")
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in {filepath}: {e}")
        raise


def check_user_conflict(email: str, filepath: str) -> bool:
    try:
        with sqlite3.connect(filepath) as connection:
            cursor = connection.cursor()

            read_query = """select 1 from client_record where email=?;
                            """

            cursor.execute(read_query, (email,))
            email_status = cursor.fetchone()
            email_status = email_status is not None

            return email_status
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error in {filepath}: {e}")
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in {filepath}: {e}")
        raise


@router.post("/api-keys")
def generate_api_keys(user: User):
    client_id = get_id(user.email)

    apikey = secrets.token_urlsafe(32)
    hashed_apikey = hashlib.sha256(apikey.encode()).hexdigest()

    filepath = settings.SQL_AUTH_DB_PATH  # "data/auth/client_record.db"
    auth_status = check_user_conflict(user.email, filepath)

    if not auth_status:
        try:
            insert_into_record(client_id, user.email, hashed_apikey, filepath)
        except sqlite3.Error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate API key. Please try again later",
            )

        return {
            "message": "Alert user! Please store the API key securely. You won't see the key again!",
            "email": user.email,
            "apikey": apikey,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not generate API key. User already exists! Please enter valid email.",
        )
