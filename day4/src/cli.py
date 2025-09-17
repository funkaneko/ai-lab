
from __future__ import annotations
import argparse, pathlib
from .openai_call import analyze_with_openai
from .anthropic_call import analyze_with_anthropic

def main():
    ap = argparse.ArgumentParser(description="Day 4: Call OpenAI/Anthropic and save normalized outputs.")
    ap.add_argument("--provider", choices=["openai", "anthropic"], required=True, help="Which API to call")
    ap.add_argument("--file", required=True, help="Path to a text file containing the policy snippet")
    args = ap.parse_args()

    snippet = pathlib.Path(args.file).read_text(encoding="utf-8")
    result = analyze_with_openai(snippet) if args.provider == "openai" else analyze_with_anthropic(snippet)
    print(result)

if __name__ == "__main__":
    main()
