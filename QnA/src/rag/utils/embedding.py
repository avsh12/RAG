import numpy as np
import requests


def embed_text(text: list[str], url: str, return_numpy: bool = False) -> list[list]:
    payload = {"content": text}
    try:
        response = requests.post(url=url, json=payload)
        status = response.status_code
        if status == 200:
            response = response.json()
            response = [x["embedding"][0] for x in response]
            if return_numpy:
                response = np.array(response)
            return response
        else:
            print(f"Server not responded. Error code: {status}")

    except Exception as e:
        print(f"Error occured while connecting to the embedding model at {url}: {e}")
