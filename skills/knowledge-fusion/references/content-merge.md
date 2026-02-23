# Content Merge Prompt

## Template

```text
整合以下 {{point_count}} 个相似知识点，生成一个完整的版本。

{{contents}}

任务:
1. 合并所有独特信息，删除重复内容
2. 确保逻辑连贯，结构清晰
3. 保留最重要的概念和细节
4. 优化语言表达

输出整合后的完整内容（保持知识点的详细程度）:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `point_count` | int | Number of similar points |
| `contents` | str | Joined source versions text |

## Notes

- Maintained as a standalone prompt template in this skillset repository.
