import sqlite3
from pathlib import Path

from api.config.config import SQL_AUTH_PATH


def get_db():
    print(SQL_AUTH_PATH)
    connection = sqlite3.connect(SQL_AUTH_PATH)
    try:
        yield connection
    finally:
        connection.close()
