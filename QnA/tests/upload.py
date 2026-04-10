import uuid

from inference.infer import fetch_context
from pipeline.upload import upload_pipeline
from qdrant_client import QdrantClient, models

filename = "data/cat-facts.txt"
raw_filepath = "~/Documents/Numerical/AI ML/Projects/RAG/QnA/data"
NAMESPACE = uuid.UUID("2f07ce7c-f5fa-4ca3-afb7-9334e47aab56")
collection_name = "cat_facts"
client = QdrantClient(path=raw_filepath)
# client.delete_collection(collection_name=collection_name)

if not client.collection_exists(collection_name=collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )
