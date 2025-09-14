import os
from dotenv import load_dotenv

def mask(key: str) -> str:
    if not key:
        return ""
    return key[:4] + "…" + key[-4:]

def main():
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    print("Environment key check (no secrets printed):")
    if openai_key:
        print(f"  ✅ OPENAI_API_KEY loaded: {mask(openai_key)}")
    else:
        print("  ❌ OPENAI_API_KEY not found")

    if anthropic_key:
        print(f"  ✅ ANTHROPIC_API_KEY loaded: {mask(anthropic_key)}")
    else:
        print("  ❌ ANTHROPIC_API_KEY not found")

    # Extra hint for venv mix-ups
    print("\nIf keys are missing:")
    print(" - Are you inside the correct virtual environment?")
    print(" - Did you create .env (copied from .env.example)?")
    print(" - Did you spell the variable names exactly?")

if __name__ == "__main__":
    main()
