from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_DIRECTORY = Path("data/models")

def load_embedding_model(
    model_name: str = DEFAULT_MODEL_NAME,
) -> SentenceTransformer:
    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)

    return SentenceTransformer(
        model_name,
        cache_folder=str(MODEL_DIRECTORY),
    )


def embed_text(
    model: SentenceTransformer,
    text: str,
) -> np.ndarray:
    return model.encode(
        text,
        convert_to_numpy=True,
    )


def embed_texts(
    model: SentenceTransformer,
    texts: list[str],
) -> np.ndarray:
    if not texts:
        return np.empty((0, model.get_sentence_embedding_dimension()))

    return model.encode(
        texts,
        convert_to_numpy=True,
    )


def cosine_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
) -> float:
    if vector_a.shape != vector_b.shape:
        raise ValueError("Vectors must have the same shape")

    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)

    if denominator == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")

    return float(np.dot(vector_a, vector_b) / denominator)


def find_top_k_similar(
    query_embedding: np.ndarray,
    candidate_embeddings: np.ndarray,
    top_k: int = 3,
) -> list[tuple[int, float]]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if candidate_embeddings.ndim != 2:
        raise ValueError("candidate_embeddings must be a two-dimensional array")

    if candidate_embeddings.shape[1] != query_embedding.shape[0]:
        raise ValueError("Query and candidate vectors must have the same dimension")

    scores = []

    for index, candidate_embedding in enumerate(candidate_embeddings):
        score = cosine_similarity(query_embedding, candidate_embedding)
        scores.append((index, score))

    scores.sort(key=lambda item: item[1], reverse=True)

    return scores[:top_k]


if __name__ == "__main__":
    model = load_embedding_model()

    documents = [
        "The appointment service creates and cancels bookings.",
        "Redis caches frequently requested data.",
        "JWT authentication validates access tokens.",
    ]

    document_embeddings = embed_texts(model, documents)
    query_embedding = embed_text(
        model,
        "Where is login token validation implemented?",
    )

    results = find_top_k_similar(
        query_embedding,
        document_embeddings,
        top_k=2,
    )

    for index, score in results:
        print(f"{score:.3f} - {documents[index]}")