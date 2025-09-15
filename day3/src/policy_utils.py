from typing import List, Dict, Any

def top_n(items: List[str], n: int = 3) -> List[str]:
    """Return first n items. If list is shorter, return all."""
    return items[:n]

def tag_risk(text: str) -> str:
    """Toy rule-based risk tagger for demo."""
    red_flags = ["privacy", "breach", "overbudget", "bias", "inequity", "fraud"]
    return "risk" if any(w in text.lower() for w in red_flags) else "ok"

def summarize_bullets(bullets: List[str]) -> Dict[str, Any]:
    """Package a summary payload like an API might."""
    return {"bullets": top_n(bullets, 3), "risk": tag_risk(" ".join(bullets))}
