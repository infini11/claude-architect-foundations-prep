"""Evaluate extract_contact() on cases.json: each output is graded by code AND by a judge model.

Usage (from the repo root):
    python3 evals/contact_extraction/run_eval.py
"""
import json
import pathlib
import sys

import anthropic
from dotenv import dotenv_values

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "src"))
from backend import make_client  # noqa: E402
from step4_structured import extract_contact  # noqa: E402  (the real function under test)

FIELDS = ["name", "email", "company", "intent", "urgent"]


# ---------- Grader 1: by code ----------
def grade_by_code(email, output, expected):
    """Correct if every field is equal (ignoring case and spaces). Return (correct, reason)."""
    # TODO 1: list the fields where the output differs from the expected value
    def clean(v):
        return v.strip().lower() if isinstance(v, str) else v
    wrong = [f for f in FIELDS if clean(output.get(f)) != clean(expected[f])]
    # TODO 2: correct = no wrong field
    return not wrong, f"wrong fields: {wrong}" if wrong else "all fields match"


# ---------- Grader 2: by a judge model ----------
JUDGE_PROMPT = """Compare the CANDIDATE extraction to the REFERENCE for this email.
It is correct if every field means the same thing: ignore case, titles (Mr., Ms.) and legal
suffixes (GmbH, Inc.). email, intent and urgent must be exactly equal. null means "not stated".

Before giving your verdict:
1. reasoning: go through the fields one by one and explain your comparison.
2. strengths: list what the candidate got right.
3. weaknesses: list what the candidate got wrong or missed (empty list if nothing).
Then set correct to true only if there is no weakness.

<email>{email}</email>
<reference>{expected}</reference>
<candidate>{output}</candidate>"""

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "correct": {"type": "boolean"},  # LAST: the judge explains first, then decides
    },
    "required": ["reasoning", "strengths", "weaknesses", "correct"],
    "additionalProperties": False,
}

# The judge always uses the real Anthropic API (even if the tested model runs on Ollama)
_env = dotenv_values(HERE.parent.parent / ".env.anthropic")
judge = anthropic.Anthropic(api_key=_env["ANTHROPIC_API_KEY"], base_url=_env["ANTHROPIC_BASE_URL"])


def grade_by_model(email, output, expected):
    """Ask Claude Haiku (not the tested model) if the output is correct. Return (correct, reason)."""
    # TODO 3: call the judge with the prompt, and force a {reasoning, strengths, weaknesses, correct} JSON answer
    response = judge.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            email=email, expected=json.dumps(expected), output=json.dumps(output))}],
        output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
    )
    # TODO 4: read the verdict
    verdict = json.loads("".join(b.text for b in response.content if b.type == "text"))
    reason = (f"\n    reasoning : {verdict['reasoning']}"
              f"\n    strengths : {verdict['strengths']}"
              f"\n    weaknesses: {verdict['weaknesses']}")
    return verdict["correct"], reason


# ---------- Run ----------
if __name__ == "__main__":
    client, model = make_client()
    cases = json.loads((HERE / "cases.json").read_text())

    code_passed = model_passed = 0
    for case in cases:
        output = extract_contact(client, case["email"], model=model)

        # the SAME output is graded twice, to compare the two approaches
        code_ok, code_reason = grade_by_code(case["email"], output, case["expected"])
        model_ok, model_reason = grade_by_model(case["email"], output, case["expected"])
        code_passed += code_ok
        model_passed += model_ok

        print(f"\n=== {case['id']} ===")
        print(f"expected : {json.dumps(case['expected'])}")
        print(f"output   : {json.dumps(output)}")
        print(f"by code  : {'PASS' if code_ok else 'FAIL'}  {code_reason}")
        print(f"by model : {'PASS' if model_ok else 'FAIL'}  {model_reason}")
        if code_ok != model_ok:
            print("           ^ the two graders disagree: which one is right?")

    n = len(cases)
    print(f"\nScore by code : {code_passed}/{n}")
    print(f"Score by model: {model_passed}/{n}")
