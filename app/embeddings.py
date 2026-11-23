
from sentence_transformers import SentenceTransformer


# BGE embedding model
MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Load model only once
model = None


def load_embedding_model():

    global model

    if model is None:
        print("Loading BGE embedding model...")

        model = SentenceTransformer(MODEL_NAME)

        print("BGE model loaded successfully!")

    return model


def generate_embeddings(texts: list[str]):

    if not texts:
        return []

    embedding_model = load_embedding_model()

    embeddings = embedding_model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings


def generate_query_embedding(query: str):

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    embedding_model = load_embedding_model()

    query = (
        "Represent this sentence for searching relevant passages: "
        + query
    )

    embedding = embedding_model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embedding
