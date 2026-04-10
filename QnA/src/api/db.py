import logging
from sqlite3 import Error, IntegrityError, connect


def create_client_record_db(filepath: str):
    try:
        with connect(filepath) as connection:
            cursor = connection.cursor()

            # --- ENABLE WAL MODE FOR HIGH CONCURRENCY ---
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            # --------------------------------------------

            create_record_query = """create table if not exists client_record(
                                    id text primary key unique,
                                    email text not null unique,
                                    hashed_api_key text not null unique);"""

            cursor.execute(create_record_query)
            connection.commit()
    except IntegrityError as e:
        logging.error(f"Integrity error while creating {filepath}: {e}")
        raise
    except Error as e:
        logging.error(f"Database error occured while creating {filepath}: {e}")
        raise
