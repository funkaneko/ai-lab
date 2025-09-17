
from __future__ import annotations
import os
from typing import Dict, Any
from .utils import load_env, write_text, write_json, coerce_json, normalize_contract, PROMPT_TEMPLATE

def analyze_with_anthropic(snippet: str) -> Dict[str, Any]:
    load_env()
    try:
        import anthropic
    except Exception as e:
        raise RuntimeError("Anthropic SDK not installed. Run: pip install anthropic") from e

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = PROMPT_TEMPLATE.replace("{snippet}", snippet)

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in getattr(msg, "content", []):
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", ""))
    text_out = "\n".join([p for p in parts if p]).strip() or str(msg)

    write_text("anthropic", text_out)
    obj = normalize_contract(coerce_json(text_out))
    write_json("anthropic", obj)
    return obj
