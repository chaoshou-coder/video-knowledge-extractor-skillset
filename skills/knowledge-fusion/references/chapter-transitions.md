# Chapter Transition Prompt

## Template

```text
为教材章节之间写一段衔接段落。

上一章 "{{prev_title}}" 的内容:
{{prev_desc}}

本章 "{{curr_title}}" 将要介绍:
{{curr_desc}}

任务:
写一段 2-3 句话的过渡段落，说明:
1. 上一章的核心收获
2. 本章与上一章的联系
3. 本章的学习价值

要求:
- 语言流畅自然
- 避免过于生硬
- 激发学习兴趣

直接输出段落内容:
```

## Variables

| Name | Type | Description |
| --- | --- | --- |
| `prev_title` | str | Previous chapter title |
| `prev_desc` | str | Previous chapter summary/description |
| `curr_title` | str | Current chapter title |
| `curr_desc` | str | Current chapter summary/description |

## Notes

- Maintained as a standalone prompt template in this skillset repository.
