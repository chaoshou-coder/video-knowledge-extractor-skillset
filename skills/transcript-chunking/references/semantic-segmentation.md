# Semantic Segmentation Prompt

## Template

```text
语义分段任务：
请你通读全文，根据主题连续性划分段落。

要求：
1) 输出 JSON，不要输出正文；
2) 每段必须包含 title、start_line、end_line；
3) start_line/end_line 使用下方行号（1 开始）；
4) 段落按出现顺序排列，尽量覆盖全文。

总行数: {{total_lines}}

文本（带行号）：
{{numbered_text}}

输出格式：
{
  "segments": [
    {"title": "段落标题", "start_line": 1, "end_line": 120}
  ]
}
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `total_lines` | int | Input text total line count |
| `numbered_text` | str | Source text with `line|content` numbering |

## Output Rules

- Return JSON only.
- Keep segment order consistent with source order.
- Prefer high coverage and avoid leaving gaps.
- Do not include narrative text outside JSON.

## Notes

- This prompt is intentionally strict to reduce downstream parser errors.
