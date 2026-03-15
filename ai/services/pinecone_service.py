from pinecone import Pinecone, ServerlessSpec

from ai.config import ai_settings
from ai.services.embedding import get_embedding

_pc = None
_index = None
INDEX_NAME = "prashikshan-question"


def _get_index():
    """Lazy-initialize the Pinecone client and index.
    Only called when AI_MOCK_MODE=false and a real Pinecone call is needed.
    """
    global _pc, _index
    if _index is not None:
        return _index

    _pc = Pinecone(api_key=ai_settings.PINECONE_API_KEY)

    if INDEX_NAME not in [index.name for index in _pc.list_indexes()]:
        _pc.create_index(
            name=INDEX_NAME,
            dimension=1024,  # must match embedding model
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    _index = _pc.Index(INDEX_NAME)
    return _index


def upsert_embeddings(text: str, record_id: str, student_id: str = None):
    try:
        vector = get_embedding(text)
        index = _get_index()

        index.upsert(
            vectors=[
                {
                    "id": record_id,
                    "values": vector,
                    "metadata": {"text": text, "student_id": student_id},
                }
            ]
        )
        return True
    except Exception as e:
        print(f"Error upserting embeddings: {str(e)}")
        return False


def query_embeddings(query_text, top_k=5, student_id=None):
    try:
        vector = get_embedding(query_text)
        index = _get_index()

        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter={"student_id": student_id},
        )
        return results
    except Exception as e:
        print(f"Error querying embeddings: {str(e)}")
        return None
