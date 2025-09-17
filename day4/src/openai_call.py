
from __future__ import annotations
import os
from typing import Dict, Any
from .utils import load_env, write_text, write_json, coerce_json, normalize_contract, PROMPT_TEMPLATE

def analyze_with_openai(snippet: str) -> Dict[str, Any]:
    load_env()
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("OpenAI SDK not installed. Run: pip install openai") from e

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PROMPT_TEMPLATE.replace("{snippet}", snippet)

    text_out = None
    try:
        resp = client.responses.create(
            model="gpt-5",
            input=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        try:
            text_out = resp.output[0].content[0].text
        except Exception:
            text_out = getattr(resp, "output_text", None)
    except Exception:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return strictly formatted JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            text_out = resp.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI call failed: {e}")

    if not text_out:
        raise RuntimeError("No text returned by OpenAI API")

    write_text("openai", text_out)
    obj = normalize_contract(coerce_json(text_out))
    write_json("openai", obj)
    return obj
