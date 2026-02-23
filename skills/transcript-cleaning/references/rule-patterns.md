# Rule Cleanup Patterns

This file stores deterministic cleanup rules used before LLM semantic cleaning.

## Pattern Table

| Order | Regex Pattern | Replacement | Purpose |
| --- | --- | --- | --- |
| 1 | `\\b(um|uh|uhh|erm|like|you know|right|so|well|okay|ok|actually|basically|literally)\\b[,.]?\\s*` | `` | Remove common English fillers |
| 2 | `(嗯+|啊+|哦+|哎+|唉+|哼+)[,，]?\\s*` | `` | Remove Chinese interjections |
| 3 | `(对吧|那个|这个|就是|然后)[,，]?\\s*` | `` | Remove common Chinese discourse particles |
| 4 | `(大家可以看到|我们来看一下|好的|那么)[,，]?\\s*` | `` | Remove low-information transitions |
| 5 | `\\n\\s*\\n\\s*\\n+` | `\\n\\n` | Collapse excessive blank lines |

## Post Rules

After applying the table above:

1. collapse repeated spaces and tabs: `[ \\t]+ -> " "`
2. trim trailing spaces before newline: ` +\\n -> \\n`
3. trim leading spaces after newline: `\\n + -> \\n`
4. if cleaned length is too short (< 30% of original), fallback to aggressive whitespace normalize only

## Notes

- Source extracted from `TextCleaner.NOISE_PATTERNS` in `src/workflow.py`.
- Keep this file synchronized with script/code fallback patterns.
