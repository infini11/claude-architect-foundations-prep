import os

import anthropic
from dotenv import load_dotenv


def chat(client, history, user_input, model, max_tokens=1000):
    """Append the user message to the history, call the model, append its reply, and return the response."""
    # 1. add the user message to the history
    history.append({"role": "user", "content": user_input})
    # 2. call the API with the WHOLE history
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=history,
    )
    # 3. add the assistant reply to the history (role "assistant", content = response.content)
    history.append({"role": "assistant", "content": response.content})
    return response


def reply_text(response):
    """Return only the text of the response (ignores thinking blocks)."""
    return "".join(block.text for block in response.content if block.type == "text")


if __name__ == "__main__":
    load_dotenv(".env.anthropic")
    client = anthropic.Anthropic()
    history = []  # the conversation memory lives HERE, in mu side

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            break
        response = chat(client, history, user_input, model=os.environ["MODEL"])
        print(f"\nClaude: {reply_text(response)}")
        print(f"[{len(history)} messages in history | {response.usage.input_tokens} input tokens]")
