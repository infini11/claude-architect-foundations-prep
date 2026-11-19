"""Structured outputs with Pydantic: the SDK builds the JSON schema AND parses the answer for you."""
from typing import Literal

from pydantic import BaseModel

from backend import make_client
from step4_structured import EMAIL


class Contact(BaseModel):
    """Replaces CONTACT_SCHEMA: the SDK turns this class into a JSON schema."""
    name: str
    email: str
    company: str
    intent: Literal["purchase", "support", "complaint", "other"]  # becomes an "enum"
    urgent: bool


def extract_contact(client, text, model, max_tokens=1000):
    """Return a typed Contact object instead of a dict."""
    response = client.messages.parse(  # parse() instead of create()
        model=model,
        max_tokens=max_tokens,
        output_format=Contact,  # a Python class instead of output_config={...}
        messages=[{
            "role": "user",
            "content": f"Extract the sender's contact information from this email:\n\n<email>\n{text}\n</email>",
        }],
    )
    return response.parsed_output  # already a Contact instance: no json.loads


if __name__ == "__main__":
    client, model = make_client()

    contact = extract_contact(client, EMAIL, model=model)
    print(contact.model_dump_json(indent=2))
    print(f"\nUrgent? {contact.urgent} | intent = {contact.intent}")  # attributes, not contact['urgent']
    print("\nSchema sent to the API:")
    print(Contact.model_json_schema())
