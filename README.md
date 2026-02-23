# video-knowledge-extractor-skillset

独立的 Agent Skillset 仓库。

这个仓库只维护 skills 资产，不包含原 extractor 的运行代码（CLI/API/模型调用编排）。

---

## 项目定位

- 目标：把「分块、清洗、结构化、视频标记、聚类、融合」能力以标准 skill 形式发布
- 用途：供任意支持 Agent Skills 的环境复用
- 设计：prompt 模板外置 + references 文档化 + scripts 可选编排

---

## Skills 列表

当前包含 6 个技能：

1. `transcript-chunking`
2. `transcript-cleaning`
3. `knowledge-extraction`
4. `video-marking`
5. `knowledge-clustering`
6. `knowledge-fusion`

每个 skill 均包含：

- `SKILL.md`（frontmatter + 指令）
- `references/*.md`（模板/规则/参考）
- `scripts/`（可选脚本）

---

## 目录结构

```text
.
├─ skills/
│  ├─ transcript-chunking/
│  ├─ transcript-cleaning/
│  ├─ knowledge-extraction/
│  ├─ video-marking/
│  ├─ knowledge-clustering/
│  └─ knowledge-fusion/
├─ tools/
│  └─ validate_skills.py
├─ examples/
│  ├─ sample1.srt
│  └─ sample2.txt
└─ .github/workflows/ci.yml
```

---

## 如何在外部项目使用

### 方式 1：作为 skills 目录直接引用

将本仓库的 `skills/` 复制或挂载到你的 Agent 项目中，然后由宿主项目按路径加载对应 skill。

### 方式 2：作为上游子模块/镜像仓库

把本仓库作为独立依赖维护，在你的主项目中按版本同步 skills 目录。

---

## 本地校验

```bash
python tools/validate_skills.py --skills-dir skills
```

这个校验会检查：

- `SKILL.md` frontmatter 必填字段
- skill 名称规范（kebab-case，且与目录同名）
- `references/` 与 `scripts/` 目录存在
- references 中模板文件的可读性

---

## examples 说明

`examples/` 中保留了通用字幕样例：

- `examples/sample1.srt`
- `examples/sample2.txt`

用途：

- skill 模板调试
- 下游集成项目联调
- CI/手动验证时的固定输入样本

---

## CI

CI 位于 `.github/workflows/ci.yml`，核心目标是保证 skills 资产结构与格式持续有效。

---

## 许可

[MIT License](./LICENSE)
