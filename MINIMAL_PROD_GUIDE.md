# Skillset 最小发布指南

本指南用于维护和发布 `video-knowledge-extractor-skillset`。

目标：保证 skills 目录结构稳定、模板可读、可被下游工程直接引用。

---

## 1) 修改 skill 资产

在 `skills/` 下新增或修改目标 skill：

- `SKILL.md`
- `references/*.md`
- `scripts/*`（可选）

建议一次变更只聚焦一个 skill。

---

## 2) 本地校验

```bash
python tools/validate_skills.py --skills-dir skills
```

若失败，优先检查：

- frontmatter 的 `name`/`description`
- `name` 与目录名是否一致
- `references/` 和 `scripts/` 是否存在

---

## 3) 样例联调

本仓库保留通用样例：

- `examples/sample1.srt`
- `examples/sample2.txt`

你可以在下游项目中用这两个样例回归技能效果，确保升级后行为可控。

---

## 4) CI 验证

提交 PR 后，CI 会执行 skills 结构校验（见 `.github/workflows/ci.yml`）。

通过标准：

- skill 校验脚本成功退出
- Python 工具脚本可编译

---

## 5) 发布建议

发布前检查清单：

1. README 已反映最新 skill 列表
2. `tools/validate_skills.py` 本地通过
3. CI 全绿
4. 变更说明清晰（新增 skill、模板调整、兼容性影响）

完成后即可打 tag 或发布 release。
