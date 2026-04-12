import logging
import sqlite3
import uuid

from pandas import DataFrame
from rag.utils.chunking import chunk


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


def create_rdb(filename: str, ID_NAMESPACE: str) -> DataFrame:
    chunked_text = chunk(filename)

    # embedded_text = embed_text(chunked_text, url)

    ids = [str(uuid.uuid5(ID_NAMESPACE, text)) for text in chunked_text]

    embedded_text = DataFrame(chunked_text, columns=["text"], index=ids).rename_axis(
        "id"
    )
    return embedded_text


def store_chunk_texts(id: str, chunks: list[str]):
    db_path = "data/user/chunked/"
