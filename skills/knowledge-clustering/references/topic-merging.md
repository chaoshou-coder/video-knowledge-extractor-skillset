# Topic Merging Prompt

## Template

```text
分析以下 {{topic_count}} 个主题，识别可以合并的相似主题。

主题列表:
{{topic_summaries}}

任务:
1. 识别标题或关键词高度相似的主题
2. 建议合并方案
3. 返回合并后的主题列表

按 JSON 输出:
{
  "merged_topics": [
    {
      "id": "topic_1",
      "title": "合并后标题",
      "description": "合并后描述",
      "original_indices": [0, 2],
      "keywords": ["关键词1", "关键词2"]
    }
  ]
}

注意:
- 只有高度相似的主题才合并
- 保持主题数量在 5-10 个
- 未合并的主题保持原样

只输出 JSON:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `topic_count` | int | Number of topics |
| `topic_summaries` | str | Joined topic summaries text |

## Notes

- Extracted from `src/clustering.py` `_merge_similar_topics`.
