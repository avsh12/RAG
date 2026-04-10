import uuid

from pandas import DataFrame
from rag.utils.chunking import chunk


def create_rdb(filename: str, ID_NAMESPACE: str) -> DataFrame:
    chunked_text = chunk(filename)

    # embedded_text = embed_text(chunked_text, url)

    ids = [str(uuid.uuid5(ID_NAMESPACE, text)) for text in chunked_text]

    embedded_text = DataFrame(chunked_text, columns=["text"], index=ids).rename_axis(
        "id"
    )
    return embedded_text
