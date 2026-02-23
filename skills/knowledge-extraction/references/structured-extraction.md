# Structured Extraction Prompt

## Template

```text
结构化提取任务：
从下述清洗后的讲座片段中提取尽可能完整的知识点，不要遗漏细节。

提取维度：
- 概念定义
- 方法步骤
- 事实信息
- 数据与结论
- 实践经验

要求：
1) 输出 JSON，字段必须是 points；
2) 每条 point 至少包含 title/content；
3) content 要保留细节，不要只写一句概括。

few-shot 示例：
{
  "points": [
    {
      "title": "强化学习在后训练中的作用",
      "content": "后训练阶段使用强化学习对模型行为进行目标对齐，关键环节包括奖励建模、策略迭代与评估闭环。该片段还强调了基础设施稳定性对实验吞吐量的影响。"
    }
  ]
}

当前片段：
{{chunk_content}}
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `chunk_content` | str | Cleaned chunk content to extract points from |

## Output Rules

- Return JSON only.
- Use `points` as the top-level field.
- Each point must include `title` and `content`.
- Keep detail density; do not over-summarize.

## Notes

- Maintained as a standalone prompt template in this skillset repository.
