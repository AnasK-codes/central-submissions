from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def get_embedding(text: str):
    try:
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None
