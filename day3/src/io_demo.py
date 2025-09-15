import json, re
from pathlib import Path
from typing import Dict, Any, List

BULLET_PREFIXES = ("- ", "* ", "• ", "· ", "— ")

def safe_load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"_error": f"Missing file: {path}"}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        return {"_error": f"Bad JSON in {path}: {e}"}

def parse_bullets_from_text(text: str) -> List[str]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    out: List[str] = []
    for ln in lines:
        raw = ln.strip()
        if not raw:
            continue
        # numeric bullets: "1) Foo", "2. Bar", "3 - Baz"
        m = re.match(r"^(\d+)[\.)\-]\s+(.*)", raw)
        if m:
            out.append(m.group(2).strip())
            continue
        # symbol bullets
        for pref in BULLET_PREFIXES:
            if raw.startswith(pref):
                out.append(raw[len(pref):].strip())
                break
    return [b for b in out if b]

def extract_bullets_from_json(data: Any) -> List[str]:
    # direct bullets
    if isinstance(data, dict):
        if isinstance(data.get("bullets"), list):
            return [str(x) for x in data["bullets"]]
        if isinstance(data.get("summary"), dict) and isinstance(data["summary"].get("bullets"), list):
            return [str(x) for x in data["summary"]["bullets"]]

        # OpenAI chat format
        msg = None
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                msg = (choice.get("message", {}) or {}).get("content") or choice.get("text")

        # Anthropic Messages format
        if msg is None and isinstance(data.get("content"), list):
            parts = []
            for block in data["content"]:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            if parts:
                msg = "\n".join(parts)

        # Fallback: top-level content
        if msg is None and isinstance(data.get("content"), str):
            msg = data["content"]

        return parse_bullets_from_text(msg) if msg else []

    if isinstance(data, list):
        out: List[str] = []
        for el in data:
            if isinstance(el, str):
                out.append(el)
            elif isinstance(el, dict):
                out.extend(extract_bullets_from_json(el))
        return out
    return []

def collect_model_bullets(outputs_dir: Path) -> List[str]:
    bullets_all: List[str] = []
    if not outputs_dir.exists():
        return bullets_all

    for p in outputs_dir.iterdir():
        if p.suffix.lower() == ".json":
            data = safe_load_json(p)
            if "_error" not in data:
                bullets_all.extend(extract_bullets_from_json(data))
        elif p.suffix.lower() == ".txt":
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            bullets_all.extend(parse_bullets_from_text(text))

    # De-duplicate while preserving order (case-insensitive)
    seen = set()
    unique: List[str] = []
    for b in bullets_all:
        s = b.strip("•*-—· ").strip()
        key = s.lower()
        if s and key not in seen:
            unique.append(s)
            seen.add(key)
    return unique
