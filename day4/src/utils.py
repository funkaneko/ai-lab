
from __future__ import annotations
import os, json, re, time, pathlib
from typing import Dict, Any
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

def load_env():
    load_dotenv(dotenv_path=ROOT / ".env")

def timestamp(prefix: str) -> str:
    return time.strftime(f"%Y%m%d_%H%M%S_{prefix}")

def write_text(prefix: str, text: str) -> str:
    p = OUT / f"{timestamp(prefix)}.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)

def write_json(prefix: str, obj: Dict[str, Any]) -> str:
    p = OUT / f"{timestamp(prefix)}.json"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)

def coerce_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    bullets, risk = [], "ok"
    for line in text.splitlines():
        s = line.strip(" -•\t")
        if not s: continue
        if s.lower().startswith("risk:"):
            tail = s.split(":", 1)[1].strip().lower()
            risk = "risk" if "risk" in tail else "ok"
        else:
            bullets.append(s)
    if not bullets: bullets = [text[:200]]
    return {"bullets": bullets[:3], "risk": risk}

def normalize_contract(obj: Dict[str, Any]) -> Dict[str, Any]:
    bullets = obj.get("bullets") or obj.get("points") or []
    if isinstance(bullets, str): bullets = [bullets]
    bullets = [str(b).strip() for b in bullets if str(b).strip()][:3]
    risk = (obj.get("risk") or obj.get("flag") or "ok").strip().lower()
    risk = "risk" if risk == "risk" else "ok"
    if not bullets and "summary" in obj: bullets = [str(obj["summary"])[:200]]
    return {"bullets": bullets or ["(no bullet)"], "risk": risk}

PROMPT_TEMPLATE = """You are a healthcare policy analysis assistant.
Return ONLY a JSON object with this exact schema:

{
  "bullets": ["<concise point 1>", "<concise point 2>", "<concise point 3>"],
  "risk": "ok" | "risk"
}

Rules:
- English only; ≤18 words per bullet.
- Set "risk" = "risk" only if there are material concerns (privacy, inequity, bias, fraud, safety, overbudget).
- No markdown fences or extra prose outside the JSON.

SNIPPET:
<<<
{snippet}
>>>
"""
