---
name: knowledge-clustering
description: Cluster merged knowledge points into topics, merge overlapping topics, and generate course chapter structure with prerequisites. Use in batch build pipelines after extraction and fusion.
license: Apache-2.0
compatibility: Works in agent environments with Markdown references. Optional script mode uses Python 3.10+.
metadata:
  author: video-knowledge-extractor-skillset
  version: "0.1.0"
  language: zh-CN
---

# Knowledge Clustering

## Purpose

Convert a flat knowledge-point set into a teachable course structure.

## Execution Modes

### Mode A: Agent-Direct

Run the three prompt templates in order:
1. `references/topic-identification.md`
2. `references/topic-merging.md`
3. `references/course-structure.md`

### Mode B: Orchestrated Script

1. Batch and summarize points.
2. Generate topics, merge similar topics, then build chapter structure.
3. Return normalized JSON for course assembly.

## Output Contracts

- Topic identification output: `topics`
- Topic merging output: `merged_topics`
- Course structure output: `course_name`, `chapters`, `prerequisites`

## References

- `references/topic-identification.md`
- `references/topic-merging.md`
- `references/course-structure.md`
