import os, sys
from pathlib import Path
from dotenv import load_dotenv
import anthropic
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
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    snippet = read_snippet(sys.argv[1] if len(sys.argv) > 1 else "samples/policy_snippet_en.txt")
    user_prompt = PROMPT_TEMPLATE.format(snippet=snippet)

    message = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=600,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # join all text blocks
    text = "".join([c.text for c in message.content if getattr(c, "type", None) == "text"])
    path = save_outputs("anthropic_response", text, message)
    print(f"Anthropic brief saved to: {path}")

if __name__ == "__main__":
    main()
