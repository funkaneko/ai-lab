import argparse, json, os
from pathlib import Path
from io_demo import collect_model_bullets
from policy_utils import summarize_bullets

def main():
    here = Path(__file__).resolve()
    # ai-lab repo root is the parent of the "day3" folder (..), then parent of "src" (../..)
    # This file lives at ai-lab/day3/src/cli.py → repo_root = parents[2]
    repo_root = here.parents[2]

    default_inputs = repo_root / "day2" / "outputs"
    default_out = repo_root / "day3" / "outputs" / "summary.json"

    ap = argparse.ArgumentParser(description="Day 3: parse day2 outputs and summarize bullets")
    ap.add_argument("--inputs", type=str, default=str(default_inputs),
                    help="Folder with JSON files from Day 2 (default: ai-lab/day2/outputs)")
    ap.add_argument("--out", type=str, default=str(default_out),
                    help="Where to write the summary JSON (default: ai-lab/day3/outputs/summary.json)")
    args = ap.parse_args()

    inputs_dir = Path(args.inputs)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bullets = collect_model_bullets(inputs_dir)
    payload = summarize_bullets(bullets)

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
