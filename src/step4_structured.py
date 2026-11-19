import json
import os

import anthropic
from dotenv import load_dotenv

# The JSON schema the answer MUST follow (standard JSON Schema syntax).
CONTACT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "company": {"type": "string"},
        "intent": {"type": "string", "enum": ["purchase", "support", "complaint", "other"]},
        "urgent": {"type": "boolean"},
    },
    "required": ["name", "email", "company", "intent", "urgent"],
    "additionalProperties": False,
}

EMAIL = """Hi, this is Eva Rossi from Nordwind GmbH (eva.rossi@nordwind.de).
Our order #1042 arrived damaged for the second time this month.
We need a replacement before Friday or we will cancel the contract."""


def extract_contact(client, text, model, max_tokens=1000):
    """Extract contact information from a free-text email and return it as a Python dict."""
    # TODO 1: call client.messages.create(...) like in step 1, with:
    #   - a user message asking to extract the contact info from `text`
    #   - output_config={"format": {"type": "json_schema", "schema": CONTACT_SCHEMA}}
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": f"Extract the sender's contact information from this email:\n\n<email>\n{text}\n</email>",
        }],
        output_config={"format": {"type": "json_schema", "schema": CONTACT_SCHEMA}}
    )
    
    #
    # TODO 2: get the text block of the response (the JSON arrives as a string)
    #   hint: reuse the logic of reply_text() from step 2
    text_block = "".join(block.text for block in response.content if block.type == "text")
    #
    # TODO 3: turn that string into a dict with json.loads(...) and return it
    return json.loads(text_block)


if __name__ == "__main__":
    load_dotenv(".env.anthropic")
    client = anthropic.Anthropic()

    contact = extract_contact(client, EMAIL, model=os.environ["MODEL"])
    print(json.dumps(contact, indent=2))
    print(f"\nUrgent? {contact['urgent']} | intent = {contact['intent']}")
