#!/usr/bin/env python3
"""
Chunk transcript text into segments/chunks.

This script is intentionally dependency-free so it can run in most
agent/script environments.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SemanticSegment:
    title: str
    start_line: int
    end_line: int
    content: str


@dataclass
class TextChunk:
    title: str
    content: str
    start_line: int
    end_line: int
    segment_index: int


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 3))


def normalize_segments(raw_segments: Any, total_lines: int) -> List[Dict[str, int | str]]:
    if not isinstance(raw_segments, list):
        return []

    parsed: List[Dict[str, int | str]] = []
    for idx, item in enumerate(raw_segments):
        if not isinstance(item, dict):
            continue
        try:
            start = int(item.get("start_line", 0))
            end = int(item.get("end_line", 0))
        except (TypeError, ValueError):
            continue
        if start <= 0 or end < start:
            continue
        start = max(1, min(start, total_lines))
        end = max(1, min(end, total_lines))
        if end < start:
            continue
        title = str(item.get("title", f"段落{idx + 1}")).strip() or f"段落{idx + 1}"
        parsed.append({"title": title, "start_line": start, "end_line": end})

    if not parsed:
        return []

    parsed.sort(key=lambda x: int(x["start_line"]))
    normalized: List[Dict[str, int | str]] = []
    cursor = 1
    for item in parsed:
        start = max(cursor, int(item["start_line"]))
        if start > total_lines:
            break
        end = min(max(start, int(item["end_line"])), total_lines)
        normalized.append({"title": str(item["title"]), "start_line": start, "end_line": end})
        cursor = end + 1
        if cursor > total_lines:
            break

    if cursor <= total_lines:
        normalized.append({"title": "尾部补全", "start_line": cursor, "end_line": total_lines})
    return normalized


def fallback_sub_chunk(segment: SemanticSegment, chunk_size: int) -> List[TextChunk]:
    lines = segment.content.splitlines()
    if not lines:
        return []

    chunks: List[TextChunk] = []
    current_lines: List[str] = []
    start_offset = 0

    def flush_chunk(end_offset: int, idx: int) -> None:
        content = "\n".join(current_lines).strip()
        if not content:
            return
        chunks.append(
            TextChunk(
                title=f"{segment.title}-子块{idx}",
                content=content,
                start_line=segment.start_line + start_offset,
                end_line=segment.start_line + end_offset,
                segment_index=0,
            )
        )

    current_tokens = 0
    chunk_idx = 1
    for i, line in enumerate(lines):
        line_tokens = estimate_tokens(line)
        next_tokens = current_tokens + line_tokens
        if current_lines and next_tokens > chunk_size:
            flush_chunk(i - 1, chunk_idx)
            chunk_idx += 1
            start_offset = i
            current_lines = [line]
            current_tokens = line_tokens
        else:
            current_lines.append(line)
            current_tokens = next_tokens

    if current_lines:
        flush_chunk(len(lines) - 1, chunk_idx)
    return chunks


def build_segments(text: str, llm_segments: Any | None = None) -> List[SemanticSegment]:
    lines = text.splitlines()
    if not lines:
        return [SemanticSegment(title="全文", start_line=1, end_line=1, content=text)]

    if llm_segments is not None:
        normalized = normalize_segments(llm_segments, len(lines))
        if normalized:
            out: List[SemanticSegment] = []
            for item in normalized:
                start = int(item["start_line"])
                end = int(item["end_line"])
                out.append(
                    SemanticSegment(
                        title=str(item["title"]),
                        start_line=start,
                        end_line=end,
                        content="\n".join(lines[start - 1 : end]),
                    )
                )
            return out

    return [
        SemanticSegment(title="全文", start_line=1, end_line=len(lines), content="\n".join(lines))
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chunk transcript text.")
    parser.add_argument("--input", required=True, help="Path to transcript text file")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=60000,
        help="Suggested max token size for each chunk",
    )
    parser.add_argument(
        "--segments-json",
        help="Optional path to LLM semantic segmentation JSON (contains segments array)",
    )
    parser.add_argument("--output", help="Optional output JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    text = input_path.read_text(encoding="utf-8")

    llm_segments: Any | None = None
    if args.segments_json:
        raw = json.loads(Path(args.segments_json).read_text(encoding="utf-8"))
        llm_segments = raw.get("segments", [])

    segments = build_segments(text, llm_segments=llm_segments)
    chunks: List[TextChunk] = []
    for segment_index, segment in enumerate(segments):
        token_count = estimate_tokens(segment.content)
        if token_count <= args.chunk_size:
            chunks.append(
                TextChunk(
                    title=segment.title,
                    content=segment.content,
                    start_line=segment.start_line,
                    end_line=segment.end_line,
                    segment_index=segment_index,
                )
            )
            continue

        subchunks = fallback_sub_chunk(segment, chunk_size=args.chunk_size)
        for c in subchunks:
            c.segment_index = segment_index
        chunks.extend(subchunks)

    payload = {
        "segments": [
            {"title": s.title, "start_line": s.start_line, "end_line": s.end_line}
            for s in segments
        ],
        "chunks": [asdict(c) for c in chunks],
    }

    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
