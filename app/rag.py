from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from embeddings import embed_text
from llm import generate_response
from vector_store import search_chunks


def answer_question(
    client: QdrantClient,
    model: SentenceTransformer,
    question: str,
    top_k: int = 3,
) -> str:
    query_embedding = embed_text(model, question)

    results = search_chunks(
        client,
        query_embedding,
        top_k=top_k,
    )

    print("\nRetrieved chunks:")

    for i, result in enumerate(results, start=1):
        print(
            f"\n{i}. {result.file_path.as_posix()}"
            f" | Lines {result.start_line}-{result.end_line}"
            f" | Score: {result.score:.3f}"
        )

    context_parts = []

    for result in results:
        context_parts.append(
            f"""File: {result.file_path.as_posix()}
Language: {result.language}
Lines: {result.start_line}-{result.end_line}
Similarity: {result.score:.3f}

{result.content}"""
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a codebase analysis assistant.

Answer the user's question using only the repository
context provided below.

If the context does not contain enough information to
answer the question, say that the information was not
found in the retrieved repository context.

Mention relevant file paths and line ranges when possible.

Repository context:
{context}

User question:
{question}
"""

    return generate_response(prompt)