---
name: knowledge-extraction
description: Extract detailed knowledge points from cleaned transcript chunks and return structured JSON fields for downstream indexing, clustering, and export. Use after transcript chunking and cleaning.
license: Apache-2.0
compatibility: Works in agent environments with Markdown references. Optional script mode uses Python 3.10+.
metadata:
  author: video-knowledge-extractor
  version: "0.1.0"
  language: zh-CN
---

# Knowledge Extraction

## Purpose

Transform cleaned transcript chunks into structured knowledge points while preserving factual and procedural detail.

## Execution Modes

### Mode A: Agent-Direct

1. Read `references/structured-extraction.md`.
2. Fill variables and run extraction prompt.
3. Return strict JSON list under `points`.

### Mode B: Orchestrated Script

1. Load cleaned chunks from file or pipeline input.
2. Apply prompt template from `references/structured-extraction.md`.
3. Validate JSON, normalize title/content fields, and return points.

## Output Contract

```json
{
  "points": [
    { "title": "知识点标题", "content": "知识点详细内容" }
  ]
}
```

## References

- `references/structured-extraction.md`
