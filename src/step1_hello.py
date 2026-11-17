import os 

import anthropic
from dotenv import load_dotenv

def ask(client, question, model, max_token=1000):
    """Send a single question to the model and return the complete response (Message)."""
    
    return client.messages.create(
        model=model,
        max_tokens=max_token,
        messages=[{"role": "user", "content": question}],
    )

if __name__ == "__main__":
    load_dotenv(".env.anthropic")
    client = anthropic.Anthropic()

    response = ask(client, "What do you think of the “Claude Certified Architect - Foundations” certification? Is it difficult to earn ?", model=os.environ["MODEL"])
    
    print(response.model_dump_json(indent=2))