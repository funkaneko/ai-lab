import os, sys
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from utils import save_outputs

PROMPT_TEMPLATE = """You are a bilingual (EN/JP) healthcare policy analyst.
Read the policy snippet below and produce a concise brief with:
- 3 bullet points (problem, intervention, measurable outcome)
- A one-line risk note (equity or ops risk)
Return English only.

POLICY SNIPPET:
{snippet}
"""

def read_snippet(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Snippet file not found: {p}")
    return p.read_text(encoding="utf-8")

def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    snippet = read_snippet(sys.argv[1] if len(sys.argv) > 1 else "samples/policy_snippet_en.txt")
    user_prompt = PROMPT_TEMPLATE.format(snippet=snippet)

    # Prefer Responses API; fall back to Chat Completions if needed
    try:
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            input=user_prompt,
            instructions="Keep it factual, concise, and neutral in tone."
        )
        text = resp.output_text
        path = save_outputs("openai_response", text, resp)
    except Exception:
        comp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role":"system","content":"Keep it factual, concise, and neutral in tone."},
                {"role":"user","content": user_prompt}
            ]
        )
        text = comp.choices[0].message.content
        path = save_outputs("openai_response", text, comp)

    print(f"OpenAI brief saved to: {path}")

if __name__ == "__main__":
    main()
