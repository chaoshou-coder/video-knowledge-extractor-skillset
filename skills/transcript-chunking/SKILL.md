---
name: transcript-chunking
description: Segment long transcript text into semantically coherent chunks and sub-chunks with line-aware boundaries. Use when processing lecture/video transcripts before downstream cleaning or knowledge extraction.
license: Apache-2.0
compatibility: Works in any agent environment that can read Markdown references. Optional script mode needs Python 3.10+.
metadata:
  author: video-knowledge-extractor
  version: "0.1.0"
  language: zh-CN
---

# Transcript Chunking

## What This Skill Does

This skill breaks transcript-like text into line-aware semantic segments, then optionally sub-splits oversized segments into smaller chunks while preserving order and meaning.

Typical input:
- lecture transcript
- subtitle-to-text output
- meeting notes with chronological order

Typical output:
- ordered semantic segments with `title`, `start_line`, `end_line`
- optional sub-chunks with `title`, `content`

## When To Use

Use this skill when:
- the source text is long and needs structure before cleaning/extraction
- you need stable boundaries for later citation or alignment
- you want chunk output that can be used by other pipelines

Do not use this skill when:
- text is already short and well-structured
- you only need light cleanup (use `transcript-cleaning`)

## Execution Modes

### Mode A: Agent-Direct (LLM Native)

1. Read prompt templates:
   - `references/semantic-segmentation.md`
   - `references/sub-chunking.md`
2. Fill template variables (`{{...}}`) from runtime input.
3. Run semantic segmentation first.
4. If a segment exceeds target size, run sub-chunking for that segment.
5. Return strict JSON for each stage.

### Mode B: Orchestrated Script

1. Run:
   - `python scripts/chunk_text.py --input path/to/input.txt --chunk-size 60000`
2. Script returns JSON with:
   - `segments`
   - `chunks`
3. Caller can choose:
   - use only `segments`
   - use final `chunks` as downstream input

## Workflow Guidance

1. Preserve original order of ideas.
2. Keep boundaries aligned with topic shifts rather than fixed length.
3. Do not rewrite or summarize source facts during chunking.
4. Ensure output is fully machine-parseable JSON.

## Output Contracts

### Semantic segmentation

```json
{
  "segments": [
    { "title": "段落标题", "start_line": 1, "end_line": 120 }
  ]
}
```

### Sub-chunking

```json
{
  "chunks": [
    { "title": "子块标题", "content": "子块正文" }
  ]
}
```

## References

- Prompt templates: `references/semantic-segmentation.md`, `references/sub-chunking.md`
- Script mode: `scripts/chunk_text.py`
