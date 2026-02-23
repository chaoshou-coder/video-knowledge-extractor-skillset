#!/usr/bin/env python3
"""
Validate skill folders under skills/.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEMPLATE_BLOCK_RE = re.compile(r"```(?:text|txt)?\s*\n(.*?)\n```", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Agent Skill folders.")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path("./skills"),
        help="Root skills directory",
    )
    return parser.parse_args()


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_frontmatter(skill_md_text: str) -> dict[str, str] | None:
    lines = skill_md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return None

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip() or line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = _strip_quotes(value)
    return fields


def validate_reference_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    has_template_section = "## Template" in text
    if has_template_section:
        block = TEMPLATE_BLOCK_RE.search(text)
        if not block or not block.group(1).strip():
            errors.append(f"{path}: missing non-empty fenced template block")
        return errors

    # Non-template reference docs (rules/tables/guides) are allowed.
    if len(text.strip()) < 20:
        errors.append(f"{path}: reference file is unexpectedly short")
    return errors


def validate_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_dir}: missing SKILL.md")
        return errors

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{skill_md}: invalid or missing YAML frontmatter")
        return errors

    name = fm.get("name", "").strip()
    description = fm.get("description", "").strip()

    if not name:
        errors.append(f"{skill_md}: missing required frontmatter field 'name'")
    if not description:
        errors.append(f"{skill_md}: missing required frontmatter field 'description'")

    if name:
        if not NAME_RE.match(name):
            errors.append(
                f"{skill_md}: invalid skill name '{name}' (expected lowercase kebab-case)"
            )
        if name != skill_dir.name:
            errors.append(
                f"{skill_md}: frontmatter name '{name}' must match directory '{skill_dir.name}'"
            )
        if len(name) > 64:
            errors.append(f"{skill_md}: name length must be <= 64")

    if description and len(description) > 1024:
        errors.append(f"{skill_md}: description length must be <= 1024")

    references_dir = skill_dir / "references"
    if not references_dir.exists() or not references_dir.is_dir():
        errors.append(f"{skill_dir}: missing references/ directory")
    else:
        reference_files = sorted(references_dir.glob("*.md"))
        if not reference_files:
            errors.append(f"{references_dir}: expected at least one *.md template file")
        for ref in reference_files:
            errors.extend(validate_reference_file(ref))

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists() or not scripts_dir.is_dir():
        errors.append(f"{skill_dir}: missing scripts/ directory")

    return errors


def main() -> int:
    args = parse_args()
    skills_dir: Path = args.skills_dir

    if not skills_dir.exists() or not skills_dir.is_dir():
        print(f"[FAIL] skills directory not found: {skills_dir}")
        return 1

    skill_dirs = sorted(
        [path for path in skills_dir.iterdir() if path.is_dir() and not path.name.startswith(".")]
    )
    if not skill_dirs:
        print(f"[FAIL] no skills found under: {skills_dir}")
        return 1

    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        all_errors.extend(validate_skill_dir(skill_dir))

    if all_errors:
        print("[FAIL] skill validation failed:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"[OK] validated {len(skill_dirs)} skill(s) in {skills_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
