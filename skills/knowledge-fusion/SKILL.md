---
name: knowledge-fusion
description: Confirm duplicate knowledge points, merge similar content into canonical entries, and generate chapter transition paragraphs. Use in batch build pipelines before clustering/export.
license: Apache-2.0
compatibility: Works in agent environments with Markdown references. Optional script mode uses Python 3.10+.
metadata:
  author: video-knowledge-extractor
  version: "0.1.0"
  language: zh-CN
---

# Knowledge Fusion

## Purpose

Reduce duplication and improve learning continuity across multi-document knowledge sets.

## Execution Modes

### Mode A: Agent-Direct

Run templates by stage:
1. `references/duplicate-confirmation.md`
2. `references/content-merge.md`
3. `references/chapter-transitions.md`

### Mode B: Orchestrated Script

1. Build candidate duplicate groups.
2. Confirm with LLM and merge into canonical entries.
3. Generate transition paragraphs between chapters.

## Output Contracts

- Duplicate confirmation: `is_duplicate`, `best_title`, `confidence`, `reason`
- Content merge: plain merged content
- Chapter transitions: short transition paragraph text

## References

- `references/duplicate-confirmation.md`
- `references/content-merge.md`
- `references/chapter-transitions.md`
