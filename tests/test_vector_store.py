from pathlib import Path

import numpy as np

from app.chunker import CodeChunk
from app.vector_store import (
    get_client,
    index_repository,
    search_chunks,
    store_chunks,
)


def test_store_chunks_persists_vectors_and_metadata(tmp_path):
    client = get_client(tmp_path / "qdrant_database")
    collection_name = "test_code_chunks"

    chunks = [
        CodeChunk(
            file_path=Path("src/auth.py"),
            language="python",
            start_line=1,
            end_line=2,
            content="def validate_token():\n    pass",
        ),
        CodeChunk(
            file_path=Path("src/cache.py"),
            language="python",
            start_line=1,
            end_line=2,
            content="def get_cached_value():\n    pass",
        ),
    ]

    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])

    try:
        store_chunks(
            client,
            chunks,
            embeddings,
            collection_name=collection_name,
        )

        records, _next_offset = client.scroll(
            collection_name=collection_name,
            limit=10,
            with_payload=True,
            with_vectors=False,
        )

        assert len(records) == 2
        assert {record.payload["file_path"] for record in records} == {
            "src/auth.py",
            "src/cache.py",
        }

        auth_record = next(
            record
            for record in records
            if record.payload["file_path"] == "src/auth.py"
        )

        assert auth_record.payload["language"] == "python"
        assert auth_record.payload["start_line"] == 1
        assert auth_record.payload["end_line"] == 2
        assert auth_record.payload["content"] == (
            "def validate_token():\n    pass"
        )
    finally:
        client.close()


def test_search_chunks_returns_the_most_similar_chunk(tmp_path):
    client = get_client(tmp_path / "qdrant_database")
    collection_name = "test_code_chunks"

    chunks = [
        CodeChunk(
            file_path=Path("src/auth.py"),
            language="python",
            start_line=10,
            end_line=12,
            content="def validate_token():\n    return True",
        ),
        CodeChunk(
            file_path=Path("src/cache.py"),
            language="python",
            start_line=20,
            end_line=22,
            content="def get_cached_value():\n    return None",
        ),
    ]

    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])

    try:
        store_chunks(
            client,
            chunks,
            embeddings,
            collection_name=collection_name,
        )

        results = search_chunks(
            client,
            query_embedding=np.array([1.0, 0.0, 0.0]),
            top_k=1,
            collection_name=collection_name,
        )

        assert len(results) == 1
        assert results[0].file_path.as_posix() == "src/auth.py"
        assert results[0].language == "python"
        assert results[0].start_line == 10
        assert results[0].end_line == 12
        assert results[0].content == "def validate_token():\n    return True"
        assert results[0].score > 0.99
        assert results[0].repository == "default"
    finally:
        client.close()


class FakeEmbeddingModel:
    def encode(self, texts, convert_to_numpy=True):
        return np.array([
            [1.0, 0.0, 0.0]
            for _text in texts
        ])


def test_index_repository_stores_repository_chunks(tmp_path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    source_file = repository / "auth.py"
    source_file.write_text(
        "def validate_token():\n    return True\n",
        encoding="utf-8",
    )

    client = get_client(tmp_path / "qdrant_database")
    collection_name = "test_code_chunks"

    try:
        indexed_count = index_repository(
            client,
            FakeEmbeddingModel(),
            repository,
            chunk_size=10,
            overlap=0,
            collection_name=collection_name,
        )

        results = search_chunks(
            client,
            query_embedding=np.array([1.0, 0.0, 0.0]),
            top_k=1,
            collection_name=collection_name,
        )

        assert indexed_count == 1
        assert len(results) == 1
        assert results[0].repository == "sample_repo"
        assert results[0].file_path.as_posix() == "auth.py"
        assert results[0].start_line == 1
        assert results[0].end_line == 2
        assert results[0].content == (
            "def validate_token():\n    return True"
        )
    finally:
        client.close()