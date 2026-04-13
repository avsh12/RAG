import sqlite3
from pathlib import Path

from rag.utils.config import settings


def get_db():
    connection = sqlite3.connect(settings.SQL_AUTH_DB_PATH)
    try:
        yield connection
    finally:
        connection.close()
