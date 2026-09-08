from pathlib import Path

from qdrant_client import QdrantClient, models
from uuid import NAMESPACE_URL, uuid5
from dataclasses import dataclass
import numpy as np

from sentence_transformers import SentenceTransformer

from chunker import CodeChunk, chunk_repository
from embeddings import embed_texts


COLLECTION_NAME = "code_chunks"
VECTOR_SIZE = 384
DATABASE_PATH = Path("data/qdrant")


def get_client(
    database_path: Path = DATABASE_PATH,
) -> QdrantClient:
    database_path.mkdir(parents=True, exist_ok=True)

    return QdrantClient(
        path=str(database_path),
    )


def ensure_collection(
    client: QdrantClient,
    collection_name: str = COLLECTION_NAME,
    vector_size: int = VECTOR_SIZE,
) -> None:
    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )


def store_chunks(
    client: QdrantClient,
    chunks: list[CodeChunk],
    embeddings: np.ndarray,
    collection_name: str = COLLECTION_NAME,
    repository: str = "default",
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("Each chunk must have one embedding")

    if embeddings.ndim != 2:
        raise ValueError("embeddings must be a two-dimensional array")

    if not chunks:
        return

    ensure_collection(
        client,
        collection_name=collection_name,
        vector_size=embeddings.shape[1],
    )

    points = []

    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"{repository}:{chunk.file_path.as_posix()}:"
                f"{chunk.start_line}:{chunk.end_line}",
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "file_path": chunk.file_path.as_posix(),
                    "language": chunk.language,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content,
                    "repository": repository,
                },
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )


@dataclass
class RetrievedChunk:
    repository: str
    file_path: Path
    language: str
    start_line: int
    end_line: int
    content: str
    score: float


def search_chunks(
    client: QdrantClient,
    query_embedding: np.ndarray,
    top_k: int = 3,
    collection_name: str = COLLECTION_NAME,
) -> list[RetrievedChunk]:
    if query_embedding.ndim != 1:
        raise ValueError("query_embedding must be a one-dimensional array")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    response = client.query_points(
        collection_name=collection_name,
        query=query_embedding.tolist(),
        limit=top_k,
        with_payload=True,
    )

    results = []

    for point in response.points:
        payload = point.payload

        results.append(
            RetrievedChunk(
                file_path=Path(payload["file_path"]),
                language=payload["language"],
                start_line=payload["start_line"],
                end_line=payload["end_line"],
                content=payload["content"],
                score=point.score,
                repository=payload["repository"],
            )
        )

    return results


def index_repository(
    client: QdrantClient,
    model: SentenceTransformer,
    repo_path: str | Path,
    chunk_size: int = 50,
    overlap: int = 10,
    collection_name: str = COLLECTION_NAME,
    repository_name: str | None = None,
) -> int:
    repository_root = Path(repo_path)

    chunks = chunk_repository(
        repository_root,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        return 0

    embeddings = embed_texts(
        model,
        [chunk.content for chunk in chunks],
    )

    store_chunks(
        client,
        chunks,
        embeddings,
        collection_name=collection_name,
        repository=repository_name or repository_root.name,
    )

    return len(chunks)


if __name__ == "__main__":
    from embeddings import embed_text, load_embedding_model

    client = get_client()
    model = load_embedding_model()

    indexed_count = index_repository(
        client,
        model,
        ".",
    )

    print(f"Indexed {indexed_count} chunks")

    query = "Where is repository scanning implemented?"
    query_embedding = embed_text(model, query)

    results = search_chunks(
        client,
        query_embedding,
        top_k=3,
    )

    for result in results:
        print(
            f"{result.score:.3f} - "
            f"{result.file_path.as_posix()}:"
            f"{result.start_line}-{result.end_line}"
        )

    client.close()
