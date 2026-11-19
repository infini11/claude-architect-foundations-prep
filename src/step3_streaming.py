
from backend import make_client


def chat_stream(client, history, user_input, model, max_tokens=1000):
    """Same as chat() in step 2, but prints the reply token by token while it is generated."""
    history.append({"role": "user", "content": user_input})

     # TODO 1: open the stream with a context manager:
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=history
    ) as stream:
        # TODO 2: inside the "with", loop over stream.text_stream
        for text in stream.text_stream:
            print(text, end="", flush=True)
            pass
        
        # TODO 3: still inside the "with", get the complete Message:
        response = stream.get_final_message()

    history.append({"role": "assistant", "content": response.content})
    return response


if __name__ == "__main__":
    client, model = make_client()
    history = []

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            break
        print("\nClaude: ", end="", flush=True)
        response = chat_stream(client, history, user_input, model=model)
        print(f"\n[{len(history)} messages in history | {response.usage.input_tokens} input tokens"
              f" | stop_reason={response.stop_reason}]")
