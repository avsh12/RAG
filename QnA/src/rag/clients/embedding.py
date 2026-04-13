import logging

from httpx import Client, HTTPStatusError, Limits
from numpy import array


class EmbeddingClient:
    def __init__(self, path: str = None, timeout: float = 2, limits: int = 50):
        self.session = Client(
            timeout=timeout, limits=Limits(max_keepalive_connections=limits)
        )
        self.path = path

    def embed_text(self, text: list[str], return_numpy: bool = False):
        payload = {"content": text}

        response = self.session.post(url=self.path, json=payload)

        try:
            response.raise_for_status()
        except HTTPStatusError as error:
            logging.error(f"Embedding server failed: {response.status_code}")
            raise error

        response = response.json()
        embeddings = [x["embedding"][0] for x in response]

        if return_numpy:
            embeddings = array(embeddings)
        return embeddings

    def close(self):
        self.session.close()
