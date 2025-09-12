# AI Lab – Week 1 Starter

This repo is a clean starting point for your **Week 1** plan (Cursor + GitHub + APIs + RAG later).

## Structure
```
ai-lab/
  data/
    raw/           # put source PDFs / policy docs here
    processed/     # derived/cleaned text or embeddings later
  docs/            # notes, decisions, design docs
  notebooks/       # experiments
  scripts/         # setup and utility scripts
  src/
    rag_basics/
      ingest.py    # (stub) for Day 5–6: turn docs into text/embeddings
      query.py     # (stub) for Day 6–7: simple Q&A over embeddings
  .env.example     # API key placeholders
  requirements.txt # libs you’ll install in Day 2–6
  .gitignore
  README.md
```

## Quick start (macOS/Linux)
```bash
cd ai-lab
bash scripts/setup_env.sh
source .venv/bin/activate
# then add your keys in .env (copied from .env.example)
```

## Quick start (Windows PowerShell)
```powershell
cd ai-lab
PowerShell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1
. .\.venv\Scripts\Activate.ps1
# then add your keys in .env (copied from .env.example)
```

## Next steps
- Day 2: add **OPENAI_API_KEY** and **ANTHROPIC_API_KEY** to `.env`.
- Day 4–6: flesh out `src/rag_basics/ingest.py` and `query.py`.
