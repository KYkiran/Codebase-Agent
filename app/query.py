from embeddings import load_embedding_model
from llm import generate_response
from rag import answer_question
from vector_store import get_client


def main() -> None:
    client = get_client()
    model = load_embedding_model()

    question = input("Ask about your codebase: ")

    answer = answer_question(
        client,
        model,
        question,
    )

    print("\nAnswer:\n")
    print(answer)

    client.close()


if __name__ == "__main__":
    main()