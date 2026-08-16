from __future__ import annotations

import argparse
import ast
import json
import sys

import tiktoken


def parse_tokens(raw: str) -> list[int]:
    for parser in (json.loads, ast.literal_eval):
        try:
            value = parser(raw)
            if isinstance(value, list) and all(isinstance(x, int) for x in value):
                return value
        except Exception:
            continue
    raise ValueError("Tokens must be a JSON/Python list of integers, e.g. '[1, 2, 3]'.")


def get_encoding():
    # Prefer model-based encoding for GPT-5.x; fall back to a modern base encoding.
    try:
        return tiktoken.encoding_for_model("gpt-5")
    except KeyError:
        return tiktoken.get_encoding("o200k_base")


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode GPT-5.x token IDs into text.")
    parser.add_argument(
        "tokens",
        help="Token list string like '[1, 2, 3]'.",
    )
    args = parser.parse_args()

    try:
        tokens = parse_tokens(args.tokens)
        encoding = get_encoding()
        text = encoding.decode(tokens)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
