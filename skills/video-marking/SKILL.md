---
name: video-marking
description: Analyze structured knowledge content and insert markers for points that require visual context from video (charts, derivations, animations). Use when generating study material with video-assisted hints.
license: Apache-2.0
compatibility: Works in agent environments with Markdown references. Optional script mode uses Python 3.10+.
metadata:
  author: video-knowledge-extractor
  version: "0.1.0"
  language: zh-CN
---

# Video Marking

## Purpose

Identify where textual explanation is insufficient without video visuals, and annotate content with visual-viewing markers.

## Execution Modes

### Mode A: Agent-Direct

1. Read `references/video-marking.md`.
2. Fill variables (`title`, `content`) and run prompt.
3. Return marked content text.

### Mode B: Orchestrated Script

1. Iterate extracted knowledge points.
2. For each point, run template in `references/video-marking.md`.
3. Parse marker tags and emit normalized marker objects.

## Marker Contract

Marker format in text:

`[需看视频画面: 时间范围]（图示说明）`

## References

- `references/video-marking.md`
