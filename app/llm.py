from ollama import chat


def generate_response(prompt: str) -> str:
    response = chat(
        model="qwen2.5-coder:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content


if __name__ == "__main__":
    res = generate_response("Explain what a REST API is in simple terms.")
    print(res)