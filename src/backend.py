"""Pick the backend (Anthropic API or local Ollama via LiteLLM) from the BACKEND environment variable."""
import os
import sys

import anthropic
from dotenv import load_dotenv


def make_client():
    """Load .env.<BACKEND> (default: anthropic) and return (client, model)."""
    backend = os.environ.get("BACKEND", "anthropic")  # "anthropic" or "ollama"
    env_file = f".env.{backend}"

    # override=True: the chosen file wins over variables already set in the terminal
    if not load_dotenv(env_file, override=True):
        sys.exit(f"{env_file} not found. Run from the repo root, or create it: cp {env_file}.example {env_file}")

    print(f"[backend={backend} | url={os.environ['ANTHROPIC_BASE_URL']} | model={os.environ['MODEL']}]")
    # Anthropic() reads ANTHROPIC_BASE_URL and ANTHROPIC_API_KEY: the SAME code works for both backends
    return anthropic.Anthropic(), os.environ["MODEL"]
