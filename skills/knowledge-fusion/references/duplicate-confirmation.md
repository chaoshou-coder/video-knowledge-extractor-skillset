# Duplicate Confirmation Prompt

## Template

```text
分析以下知识点，判断它们是否重复或高度相似。

知识点:
{{point_descriptions}}

任务:
1. 判断这些知识点是否重复（描述同一概念）
2. 如果是重复的，选择最佳标题
3. 给出置信度分数 (0.0-1.0)

按 JSON 输出:
{
  "is_duplicate": true,
  "best_title": "最佳标题",
  "confidence": 0.9,
  "reason": "解释原因"
}

注意:
- 标题相似但内容不同不算重复
- 同一概念的不同表述算重复
- 置信度 > 0.8 才认为是重复

只输出 JSON:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `point_descriptions` | str | Candidate point descriptions in current group |

## Notes

- Extracted from `src/fusion.py` `_confirm_duplicates`.
