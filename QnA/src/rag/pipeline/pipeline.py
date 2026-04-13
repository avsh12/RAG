from itertools import repeat

from qdrant_client import QdrantClient, models
from rag.clients.embedding import EmbeddingClient
from rag.clients.llm import LLMClient
from rag.utils.chunking import chunk


class RAG:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_client: EmbeddingClient,
        llm_client: LLMClient,
        collection_name,
    ):
        self.qdrant_client = qdrant_client
        self.embedding_client = embedding_client
        self.llm_client = llm_client
        self.collection_name = collection_name
        self.embed_dim = 768

        self.create_collection(self.collection_name)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, tb):
        self.qdrant_client.close()
        self.embedding_client.close()
        self.llm_client.close()

    def create_collection(self, collection_name: str = None):
        if collection_name is not None:
            self.collection_name = collection_name

        if not self.qdrant_client.collection_exists(
            collection_name=self.collection_name
        ):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embed_dim, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )

    def payload_generator(self, client_ids: str, filepaths: str, chunks: list[str]):
        for id, (filepath, text) in zip(client_ids, zip(filepaths, chunks)):
            yield {"client_id": id, "filepath": filepath.name, "text": text}

    def ingest(self, client_id: str, filepath: str):
        chunked_text = chunk(filepath)
        vectors = self.embedding_client.embed_text(chunked_text)

        self.qdrant_client.upload_collection(
            collection_name=self.collection_name,
            vectors=vectors,
            payload=self.payload_generator(
                repeat(client_id), repeat(filepath), chunked_text
            ),
        )

    def query_llm(self, query: str, context: list[str]):
        context = "\n".join(context)

        instruction = """Based on context provided, respond only to what the query text says or asks. 
                        If the information the query text seeks is not present in the context text, without explanation say the information is not available.
                        However, if the information contradicts, say the same."""

        contextualized_query = f"""<instruction>
                                    {instruction}
                                   </instruction>
                                    
                                   <context>
                                    {context}
                                   </context>
                                    
                                   <query>
                                    {query}
                                   </query>"""

        llm_response = self.llm_client.model(contextualized_query)[0]
        return llm_response

    def query(self, client_id: str, text: str) -> dict:
        vector = self.embedding_client.embed_text([text])[0]
        context = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="client_id", match=models.MatchValue(value=client_id)
                    )
                ]
            ),
            with_payload=True,
        )

        context = [point.payload["text"] for point in context.points]

        llm_response = self.query_llm(text, context)
        return {"content": llm_response, "context": context}

        # self.client.create_payload_index(
        #     collection_name=self.collection_name,
        #     field_name="id",
        #     field_schema=models.PayloadSchemaType.KEYWORD,
        # )
