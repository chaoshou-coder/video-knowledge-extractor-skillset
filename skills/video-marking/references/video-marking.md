# Video Marking Prompt

## Template

```text
分析以下知识点内容，判断是否需要配合视频画面才能理解：

知识点：{{point_title}}
内容：{{point_content}}

如果需要视频画面（如图表、公式推导、动画），在相关段落前插入标记：
[需看视频画面: 时间范围]（图示说明）

输出修改后的内容（如无视频需求则输出原文）：
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `point_title` | str | Knowledge point title |
| `point_content` | str | Knowledge point content |

## Output Rules

- Return updated plain text.
- If visual context is required, insert markers using exact format.
- If not required, return original text without extra commentary.

## Marker Format

`[需看视频画面: 时间范围]（图示说明）`

## Notes

- Maintained as a standalone prompt template in this skillset repository.
