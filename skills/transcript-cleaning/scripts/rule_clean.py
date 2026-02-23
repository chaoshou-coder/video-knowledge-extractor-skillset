#!/usr/bin/env python3
"""
Deterministic transcript cleanup script.

This script mirrors TextCleaner behavior and keeps external dependencies at zero.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NOISE_PATTERNS = [
    (
        r"\b(um|uh|uhh|erm|like|you know|right|so|well|okay|ok|actually|basically|literally)\b[,.]?\s*",
        "",
    ),
    (r"(嗯+|啊+|哦+|哎+|唉+|哼+)[,，]?\s*", ""),
    (r"(对吧|那个|这个|就是|然后)[,，]?\s*", ""),
    (r"(大家可以看到|我们来看一下|好的|那么)[,，]?\s*", ""),
    (r"\n\s*\n\s*\n+", "\n\n"),
]


def clean_text(text: str) -> str:
    original_length = len(text)
    for pattern, replacement in NOISE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n +", "\n", text)

    if len(text) < original_length * 0.3:
        text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic transcript cleanup.")
    parser.add_argument("--input", help="Input text file path. If omitted, reads stdin.")
    parser.add_argument("--output", help="Output text file path. If omitted, writes stdout.")
    return parser.parse_args()


def read_input(input_path: str | None) -> str:
    if input_path:
        return Path(input_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def write_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def main() -> int:
    args = parse_args()
    source = read_input(args.input)
    cleaned = clean_text(source)
    write_output(cleaned, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
