"""
Prompt loader for skill-based prompt templates.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict


_PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


class PromptLoader:
    """Load and render prompt templates from skill references."""

    def __init__(self, skills_dir: str | Path | None = None):
        if skills_dir is None:
            self.skills_dir = Path(__file__).resolve().parent.parent / "skills"
        else:
            self.skills_dir = Path(skills_dir)
        self._template_cache: Dict[Path, str] = {}

    def load(self, skill_name: str, reference_name: str, **variables: Any) -> str:
        path = self._reference_path(skill_name=skill_name, reference_name=reference_name)
        if path not in self._template_cache:
            markdown = path.read_text(encoding="utf-8")
            self._template_cache[path] = self._extract_template(markdown)
        template = self._template_cache[path]
        return self._render(template, variables)

    def exists(self, skill_name: str, reference_name: str) -> bool:
        return self._reference_path(skill_name=skill_name, reference_name=reference_name).exists()

    def _reference_path(self, skill_name: str, reference_name: str) -> Path:
        return self.skills_dir / skill_name / "references" / f"{reference_name}.md"

    @staticmethod
    def _extract_template(markdown: str) -> str:
        template_section = markdown
        section_match = re.search(r"(?im)^##\s*Template\s*$", markdown)
        if section_match:
            template_section = markdown[section_match.end() :]

        fenced = re.search(r"```(?:text|txt)?\s*\n(.*?)\n```", template_section, flags=re.DOTALL)
        if fenced:
            return fenced.group(1).strip()

        return template_section.strip()

    @staticmethod
    def _render(template: str, variables: Dict[str, Any]) -> str:
        missing_keys: set[str] = set()

        def _replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in variables:
                missing_keys.add(key)
                return match.group(0)
            return str(variables[key])

        rendered = _PLACEHOLDER_RE.sub(_replace, template)
        if missing_keys:
            missing_str = ", ".join(sorted(missing_keys))
            raise KeyError(f"Missing prompt template variable(s): {missing_str}")
        return rendered
