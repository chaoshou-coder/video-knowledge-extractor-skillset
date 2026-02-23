# Course Structure Prompt

## Template

```text
基于以下 {{topic_count}} 个主题，设计教材的章节结构。

主题列表:
{{topic_summaries}}

任务:
1. 将主题组织为教材章节（3-8章）
2. 确定章节顺序（考虑知识依赖关系）
3. 识别章节间的前置关系

按 JSON 输出:
{
  "course_name": "课程名称（简洁专业）",
  "chapters": [
    {
      "order": 1,
      "title": "章节标题",
      "topic_ids": ["topic_1", "topic_2"],
      "description": "章节描述",
      "learning_objectives": ["目标1", "目标2"]
    }
  ],
  "prerequisites": {
    "章节标题": ["前置章节标题1", "前置章节标题2"]
  }
}

注意:
- 章节标题要专业、清晰
- 考虑知识点的逻辑依赖
- 每章包含2-4个相关主题
- 前置关系要合理

只输出 JSON:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `topic_count` | int | Number of topics |
| `topic_summaries` | str | Joined topic summaries text |

## Notes

- Maintained as a standalone prompt template in this skillset repository.
