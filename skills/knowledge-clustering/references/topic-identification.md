# Topic Identification Prompt

## Template

```text
分析以下 {{point_count}} 个知识点，识别其中的主题聚类。

知识点列表:
{{point_summaries}}

任务:
1. 识别主要主题（3-10个主题）
2. 为每个主题确定:
   - 主题名称（简洁明确）
   - 主题描述（1-2句话）
   - 包含的知识点索引
   - 关键词（3-5个）

按以下 JSON 格式输出:
{
  "topics": [
    {
      "id": "topic_1",
      "title": "主题名称",
      "description": "主题描述",
      "point_indices": [0, 1, 2],
      "keywords": ["关键词1", "关键词2"]
    }
  ]
}

注意:
- 一个知识点可以属于多个主题
- 主题应该有明确的边界，避免过度重叠
- 按重要性排序主题

只输出 JSON，不要有其他内容:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `point_count` | int | Number of points in current batch |
| `point_summaries` | str | Joined point summaries text |

## Notes

- Maintained as a standalone prompt template in this skillset repository.
