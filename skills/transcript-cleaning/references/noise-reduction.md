# Noise Reduction Prompt

## Template

```text
清洗任务：
请清洗以下文本片段，删除口水话但保留信息细节。

要求：
1) 仅删除语气词、寒暄、重复强调和无信息量过渡句；
2) 保留所有事实、观点、术语、方法、数据、论据；
3) 不要摘要，不要改写逻辑顺序；

片段：
{{chunk_content}}
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `chunk_content` | str | Text chunk to clean |

## Output Rules

- Return cleaned plain text only.
- Keep key details and original reasoning sequence.
- Never return an abstract summary.

## Notes

- Source extracted from `src/workflow.py` noise reduction stage.
- Caller may enforce a minimum output length ratio for quality control.
