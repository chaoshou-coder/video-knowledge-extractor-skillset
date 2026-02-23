---
name: transcript-cleaning
description: Clean noisy transcript text by removing filler words and low-information chatter while preserving facts, terminology, and reasoning details. Use after chunking and before structured extraction.
license: Apache-2.0
compatibility: Works in agent environments with Markdown reading. Optional script mode needs Python 3.10+.
metadata:
  author: video-knowledge-extractor-skillset
  version: "0.1.0"
  language: zh-CN
---

# Transcript Cleaning

## What This Skill Does

This skill removes noise from transcript text using two layers:
- deterministic rule cleanup (filler words, repeated discourse markers, excessive spacing)
- LLM semantic cleanup (remove low-information chatter while preserving details)

## When To Use

Use this skill when:
- transcript quality is noisy or conversational
- you need cleaner text before extraction/indexing
- you must preserve factual and procedural detail

Do not use this skill when:
- source text is already concise and formal
- strong compression/summarization is desired (this skill is not a summarizer)

## Execution Modes

### Mode A: Agent-Direct (LLM Native)

1. Optionally apply deterministic cleanup using `references/rule-patterns.md`.
2. Read `references/noise-reduction.md`.
3. Fill template variable(s), then run cleanup prompt.
4. Validate output:
   - content should not be empty
   - length should not collapse abnormally
   - keep core facts and methods intact

### Mode B: Orchestrated Script

1. Run deterministic stage:
   - `python scripts/rule_clean.py --input path/to/input.txt`
2. (Optional) run LLM semantic cleanup with prompt template:
   - `references/noise-reduction.md`
3. Combine both stages based on quality checks.

## Guardrails

- Remove tone fillers, not information.
- Keep terminology, numbers, methods, claims, and evidence.
- Do not reorder logic.
- Do not convert to summary style.

## Output Contract

- Return plain cleaned text for cleaning stage.
- If running in JSON-oriented pipelines, wrap externally; this skill itself focuses on text payload.

## References

- LLM prompt template: `references/noise-reduction.md`
- Rule patterns: `references/rule-patterns.md`
- Deterministic script: `scripts/rule_clean.py`
