import numpy as np
import pytest

from app.embeddings import cosine_similarity, find_top_k_similar


def test_cosine_similarity_returns_one_for_identical_vectors():
    vector = np.array([1.0, 2.0, 3.0])

    assert cosine_similarity(vector, vector) == pytest.approx(1.0)


def test_cosine_similarity_returns_zero_for_orthogonal_vectors():
    vector_a = np.array([1.0, 0.0])
    vector_b = np.array([0.0, 1.0])

    assert cosine_similarity(vector_a, vector_b) == pytest.approx(0.0)


def test_cosine_similarity_rejects_different_vector_shapes():
    vector_a = np.array([1.0, 2.0])
    vector_b = np.array([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        cosine_similarity(vector_a, vector_b)


def test_cosine_similarity_rejects_zero_vectors():
    zero_vector = np.array([0.0, 0.0])
    other_vector = np.array([1.0, 1.0])

    with pytest.raises(ValueError):
        cosine_similarity(zero_vector, other_vector)


def test_find_top_k_similar_returns_results_in_descending_order():
    query_embedding = np.array([1.0, 0.0])

    candidate_embeddings = np.array([
        [0.0, 1.0],   # index 0: unrelated
        [1.0, 0.1],   # index 1: most similar
        [-1.0, 0.0],  # index 2: opposite
    ])

    results = find_top_k_similar(
        query_embedding,
        candidate_embeddings,
        top_k=2,
    )

    assert [index for index, _score in results] == [1, 0]
    assert results[0][1] > results[1][1]


def test_find_top_k_similar_rejects_invalid_top_k():
    query_embedding = np.array([1.0, 0.0])
    candidate_embeddings = np.array([[1.0, 0.0]])

    with pytest.raises(ValueError):
        find_top_k_similar(
            query_embedding,
            candidate_embeddings,
            top_k=0,
        )