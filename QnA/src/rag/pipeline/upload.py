from qdrant_client import QdrantClient
from rag.utils.embedding import embed_text
from rag.utils.raw_database import create_rdb


def upload_pipeline(
    raw_filename: str, ID_NAMESPACE: str, client: QdrantClient, collection_name: str
):
    text_db = create_rdb(raw_filename, ID_NAMESPACE)

    raw_filepath = "~/Documents/Numerical/AI ML/Projects/RAG/QnA/data/cat_facts.parquet"
    text_db.to_parquet(raw_filepath)

    emb_url = "http://localhost:8181/embedding"
    vectors = embed_text(text_db.text.values.tolist(), emb_url)

    client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        ids=text_db.index.to_list(),
        update_mode="insert_only",
    )
