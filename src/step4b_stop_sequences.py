"""Old-school JSON extraction: XML tags in the prompt + stop_sequences. Nothing is guaranteed."""
import json

from backend import make_client
from step4_structured import EMAIL


def extract_contact(client, text, model, max_tokens=1000):
    """Ask for JSON between <json> tags, stop generation at </json>, then parse it ourselves."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        stop_sequences=["</json>"],  # generation stops HERE; "</json>" is NOT included in the output
        messages=[{
            "role": "user",
            "content": (
                "Extract the sender's contact information from this email.\n"
                "Fields: name, email, company, intent (purchase|support|complaint|other), urgent (boolean).\n"
                "Write ONLY the JSON object between <json> and </json>.\n\n"
                f"<email>\n{text}\n</email>"
            ),
        }],
    )
    print(f"stop_reason={response.stop_reason} | stop_sequence={response.stop_sequence!r}")

    raw = "".join(block.text for block in response.content if block.type == "text")
    print("\n----- 1. RAW TEXT (exactly what the model returned) -----")
    print(raw)
    print("----- (repr, to see hidden \\n and spaces) -----")
    print(repr(raw))

    # Manual work the structured outputs did for us: cut after <json>, then hope it's valid JSON.
    json_text = raw.split("<json>", 1)[-1].strip()
    print("\n----- 2. AFTER EXTRACTION (what we give to json.loads) -----")
    print(json_text)
    print("\n----- 3. PARSED DICT -----")
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"The model did not return valid JSON: {e}") from e


if __name__ == "__main__":
    client, model = make_client()

    contact = extract_contact(client, EMAIL, model=model)
    print(json.dumps(contact, indent=2))
