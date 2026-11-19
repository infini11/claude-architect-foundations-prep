
from backend import make_client

def ask(client, question, model, max_token=1000):
    """Send a single question to the model and return the complete response (Message)."""
    
    return client.messages.create(
        model=model,
        max_tokens=max_token,
        messages=[{"role": "user", "content": question}],
    )

if __name__ == "__main__":
    client, model = make_client()

    response = ask(client, "What do you think of the “Claude Certified Architect - Foundations” certification? Is it difficult to earn ?", model=model)
    
    print(response.model_dump_json(indent=2))