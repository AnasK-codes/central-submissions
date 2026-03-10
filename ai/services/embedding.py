# Lazy loading to avoid slow server startup
_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    return _model

def get_embedding(text:str):
    try:
        model = _get_model()
        embedding=model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

