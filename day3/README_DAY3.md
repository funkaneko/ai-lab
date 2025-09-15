# Day 3 — Python Fundamentals for AI

This folder is designed to live at: `~/Projects/ai-lab/day3/`.
The defaults in the code read files from `~/Projects/ai-lab/day2/outputs/`
and write a new summary to `~/Projects/ai-lab/day3/outputs/summary.json`.

**Supported input formats (in `day2/outputs/`):**
- `*.json` — raw API responses (OpenAI/Anthropic or custom). The loader can parse:
  - direct `{"bullets": [...]}`
  - nested `{"summary": {"bullets": [...]}}`
  - OpenAI chat shapes (extracts `message.content` then parses bullets from text)
  - Anthropic messages shapes (extracts text blocks then parses bullets)
- `*.txt` — human‑readable outputs. Any lines like `- ...`, `• ...`, or `1) ...` become bullets.

## Run locally

```bash
cd ~/Projects/ai-lab/day3
# (optional) python3 -m venv .venv && source .venv/bin/activate

# warm-up
python src/basics.py

# main flow (reads ai-lab/day2/outputs/*.{json,txt}, writes ai-lab/day3/outputs/summary.json)
python src/cli.py
# or specify paths explicitly
python src/cli.py --inputs ~/Projects/ai-lab/day2/outputs --out ~/Projects/ai-lab/day3/outputs/summary.json
```

## Files
- `src/basics.py` — variables, lists, dicts
- `src/policy_utils.py` — tiny helpers: `top_n`, `tag_risk`, `summarize_bullets`
- `src/io_demo.py` — safe JSON/TXT loading + collecting bullets from multiple files
- `src/cli.py` — ties it together; defaults wired to the `ai-lab` root

## Notes
- If `day2/outputs` is empty on your machine, drop a sample JSON there.
  Example shape:
  ```json
  {"bullets": ["Expand rural coverage", "Outcome tracking", "Quarterly budget review"]}
  ```
- Error handling is deliberately light and user-friendly so the script keeps running.
