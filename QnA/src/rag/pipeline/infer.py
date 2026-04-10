import os
import uuid
from contextlib import closing

import requests
from pandas import DataFrame, read_parquet
from qdrant_client import QdrantClient, models
from rag.pipeline.upload import upload_pipeline
from rag.utils.embedding import embed_text


def query_vector(
    query_vectors: list[list], vector_db: QdrantClient, collection_name: str
):
    query_requests = [models.QueryRequest(query=vector) for vector in query_vectors]
    query_response = vector_db.query_batch_points(
        collection_name=collection_name, requests=query_requests
    )

    return query_response


def fetch_context(
    query: list[str],
    db: DataFrame,
    vector_db: QdrantClient,
    collection_name: str,
    url: str,
) -> list[DataFrame]:
    query_vectors = embed_text(query, url=url)

    query_response = query_vector(query_vectors, vector_db, collection_name)

    query_response = [
        DataFrame(
            [[point.id, point.score] for point in x.points], columns=["id", "score"]
        ).set_index("id")
        for x in query_response
    ]

    contexts = [response.join(db, on="id", how="left") for response in query_response]
    return contexts


def model(query: str, url: str) -> str:
    payload = {"messages": [{"role": "user", "content": query}], "streams": False}
    try:
        model_response = requests.post(url=url, json=payload)
        status = model_response.status_code
        if status == 200:
            model_response = model_response.json()
            model_response = [
                response["message"]["content"] for response in model_response["choices"]
            ]
            return model_response

        else:
            print("Model didn't respond.")
    except Exception as e:
        print(f"Exception occured while connecting to the model server at {url}: {e}")


def infer_model(queries: list[str]):
    collection_name = "cat_facts"
    raw_filepath = os.path.expanduser(
        "~/Documents/Numerical/AI ML/Projects/RAG/QnA/data/"
    )
    emb_url = "http://localhost:8181/embedding"
    model_url = "http://localhost:8080/v1/chat/completions"

    db = read_parquet(os.path.join(raw_filepath, "cat_facts.parquet"))
    with closing(QdrantClient(path=raw_filepath)) as client:
        contexts = fetch_context(queries, db, client, collection_name, emb_url)
        contexts = [context.text.values.tolist() for context in contexts]
        contexts = ["\n".join(context) for context in contexts]

        instruction = """Based on context provided, respond only to what the query text says or asks. 
                        If the information the query text seeks is not present in the context text, without explanation say the information is not available.
                        However, if the information contradicts, say the same."""

        contextualized_query = [
            f"""<instruction>
                    {instruction}
                </instruction>
                                    
                <context>
                    {context}
                </context>
                                    
                <query>
                    {query}
                </query>"""
            for (query, context) in zip(queries, contexts)
        ]

        responses = [model(query, model_url) for query in contextualized_query]
        return responses


if __name__ == "__main__":
    # filename = "data/cat-facts.txt"
    # raw_filepath = os.path.expanduser(
    #     "~/Documents/Numerical/AI ML/Projects/RAG/QnA/data"
    # )
    # NAMESPACE = uuid.UUID("2f07ce7c-f5fa-4ca3-afb7-9334e47aab56")
    # collection_name = "cat_facts"
    # emb_url = "http://localhost:8181/embedding"

    # with closing(QdrantClient(path=raw_filepath)) as client:
    #     # client.delete_collection(collection_name=collection_name)

    #     if not client.collection_exists(collection_name=collection_name):
    #         client.create_collection(
    #             collection_name=collection_name,
    #             vectors_config=models.VectorParams(
    #                 size=768, distance=models.Distance.COSINE
    #             ),
    #         )
    #         upload_pipeline(filename, NAMESPACE, client, collection_name)

    #     query = [
    #         "How long can cats live?",
    #         "Who pet the cats first?",
    #         "Why Egyptians aren't the first to pet cats?",
    #     ]

    #     db = read_parquet(raw_filepath + "/cat_facts.parquet")
    #     response = fetch_context(query, db, client, collection_name, emb_url)

    # print(response)
    queries = [
        "How long can cats live?",
        "Who pet the cats first?",
        "Why Egyptians aren't the first to pet cats?",
    ]
    response = infer_model(queries)
    print(response)
