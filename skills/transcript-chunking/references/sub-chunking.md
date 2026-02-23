# Sub-chunking Prompt

## Template

```text
子切分任务：
以下是一个语义连续的大段内容，请按内容边界再切分为多个子块。

约束：
1) 每个子块建议不超过 {{chunk_size}} token；
2) 必须保持原始顺序，不能改写事实；
3) 必须输出每个子块的具体内容；
4) 只输出 JSON。

输出格式：
{
  "chunks": [
    {"title": "子块标题", "content": "子块正文"}
  ]
}

原段标题：{{segment_title}}
原段行号：{{segment_start_line}}-{{segment_end_line}}

原段内容：
{{segment_content}}
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `chunk_size` | int | Suggested max token length per chunk |
| `segment_title` | str | Source segment title |
| `segment_start_line` | int | Segment start line number |
| `segment_end_line` | int | Segment end line number |
| `segment_content` | str | Full segment text to split |

## Output Rules

- Return JSON only.
- Keep source ordering.
- Preserve facts without paraphrasing.
- Include concrete `content` for every chunk.

## Notes

- Caller should run this only for oversized segments.
