# Contributing to video-knowledge-extractor-skillset

感谢你为本仓库贡献 Agent Skills。

本仓库是**纯 skill 资产仓库**，不接受 extractor 运行时代码（CLI/API/模型网关）改动。

---

## 本地准备

```bash
git clone https://github.com/chaoshou-coder/video-knowledge-extractor-skillset.git
cd video-knowledge-extractor-skillset
```

---

## Skill 目录规范

每个 skill 目录必须满足：

```text
skills/<skill-name>/
├─ SKILL.md
├─ references/
└─ scripts/
```

规则：

- `<skill-name>` 使用小写 kebab-case
- `SKILL.md` frontmatter 至少包含：
  - `name`
  - `description`
- frontmatter 中 `name` 必须与目录名一致

---

## references 规范

- prompt 模板文件建议包含 `## Template` 段落和 fenced block
- 非模板型文档（规则表/说明文档）可不含模板块，但内容需清晰可读

---

## scripts 规范

- `scripts/` 目录必须存在
- 脚本应可独立运行，避免隐式依赖
- 为脚本补充必要注释和参数说明

---

## 提交前检查

```bash
python tools/validate_skills.py --skills-dir skills
```

如果校验失败，请先修复结构或 frontmatter 问题再提交 PR。

---

## Pull Request 建议

- 一次 PR 聚焦一个 skill 或一个主题变更
- 在 PR 描述中写明：
  - 变更的 skill 目录
  - 影响的 references/scripts
  - 兼容性说明（如有）

---

## 不在本仓库范围

以下内容请提交到独立的 extractor 工程仓库：

- 运行时处理流程实现
- CLI 参数与执行逻辑
- 模型 provider 接入代码
- 导出器与数据库逻辑
