# Day 2 — API Setup & First Integration

You’ll wire up **OpenAI** and **Anthropic** in your project, using a `.env` file so secrets stay out of Git.

---

## 1) One-time install (inside your project venv)

```bash
pip install --upgrade openai anthropic python-dotenv
```

> Mental model: your API keys are **keys to the archive building**. The `.env` file is the **safe** behind the counter. Never push the safe to GitHub.

---

## 2) Create your secrets file

1. Duplicate `.env.example` → rename to `.env`
2. Paste your keys:
   - Get **OpenAI** key: https://platform.openai.com/api-keys
   - Get **Anthropic** key: https://console.anthropic.com
3. Keep `.env` private (already in `.gitignore`).

---

## 3) Sanity check (no secrets printed)

```bash
python src/check_env.py
```

You should see ✅ for each provider, plus the last 4 characters of your key for verification.

---

## 4) Your first API calls (policy-flavoured examples)

OpenAI:
```bash
python src/test_openai.py samples/policy_snippet_en.txt
```

Anthropic:
```bash
python src/test_anthropic.py samples/policy_snippet_en.txt
```

Outputs are saved to the `outputs/` folder as both `.txt` and `.json` with timestamps.

---

## 5) What these scripts do (in plain terms)

- Load keys from `.env` using `python-dotenv`
- Read a short **policy snippet** (you can replace with your own)
- Ask the model to produce a concise **3-bullet brief** (policy analyst style)
- Save responses to disk for your records and reproducibility

---

## 6) Good habits you already know (policy ↔ engineering)

- **Separate powers**: code vs. secrets (`.env`)
- **Audit trail**: outputs saved with timestamps = evidence for decisions
- **Small experiments**: tweak one variable at a time (prompt, model, max tokens)

---

## 7) Next steps (Day 3 preview)

- Python function basics using health/policy examples
- Light JSON handling for API responses
- Guardrails: minimal error handling patterns

---

**Tip**: If a call fails, run `python src/check_env.py` again and confirm you’re inside the venv you used to install packages.
