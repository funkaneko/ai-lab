# Changelog — Day 3 (ai-lab)

## Patch: robust bullet extraction
- `src/io_demo.py`: now parses both JSON and TXT outputs from `day2/outputs/`.
  Supports common OpenAI (`choices[0].message.content`) and Anthropic (content blocks) shapes.
  Also handles simple `{"bullets":[...]}` and `{"summary":{"bullets":[...]}}`.
- `README_DAY3.md`: documented supported input formats.
