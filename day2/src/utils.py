import os, json, datetime, pathlib

def save_outputs(prefix: str, text: str, raw_obj) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = pathlib.Path(__file__).resolve().parent.parent / "outputs"
    base.mkdir(parents=True, exist_ok=True)

    txt_path = base / f"{prefix}_{ts}.txt"
    json_path = base / f"{prefix}_{ts}.json"

    txt_path.write_text(text, encoding="utf-8")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            if hasattr(raw_obj, "model_dump"):
                json.dump(raw_obj.model_dump(), f, ensure_ascii=False, indent=2)
            else:
                # fall back to str() for non-pydantic objects
                json.dump(json.loads(str(raw_obj)), f, ensure_ascii=False, indent=2)
    except Exception:
        # last resort: serialize best-effort
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"repr": repr(raw_obj)}, f, ensure_ascii=False, indent=2)

    return str(txt_path)
