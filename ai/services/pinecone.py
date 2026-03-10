from pinecone import Pinecone, ServerlessSpec

from app.core.config import PINECONE_API_KEY
from app.services.embedding import get_embedding

# Lazy initialization to avoid slow startup
_pc = None
_index = None
index_name = "prashikshan-question"


def _get_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
        if not _pc.has_index(index_name):
            _pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        _index = _pc.Index(index_name)
    return _index


def upsert_embeddings(text: str, record_id: str, student_id: str = None):
    try:
        index = _get_index()
        vector = get_embedding(text)
        print(f"[Pinecone Service] Generated embedding vector of dimension: {len(vector)}")

        result = index.upsert(
            vectors=[
                {
                    "id": record_id,
                    "values": vector,
                    "metadata": {
                        "text": text,
                        "student_id": student_id
                    }
                }
            ]
        )
        print(f"[Pinecone Service] Upsert response: {result}")
        return {"success": True, "upserted_count": result.get("upserted_count", 1)}
    except Exception as e:
        print(f"Error upserting embeddings: {str(e)}")
        return {"success": False, "error": str(e)}
  


def query_embeddings(query_text, top_k=5, student_id=None):
    try:
        index = _get_index()
        vector = get_embedding(query_text)

        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter={
                "student_id": student_id
            }
        )
        return results
    except Exception as e:
        print(f"Error querying embeddings: {str(e)}")
        return None