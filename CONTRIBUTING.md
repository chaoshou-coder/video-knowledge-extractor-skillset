# Contributing to Video Knowledge Extractor Skillset

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/chaoshou-coder/video-knowledge-extractor-skillset.git
cd video-knowledge-extractor-skillset
pip install -e .
```

## Running Local Checks

```bash
# Syntax check
python -m compileall src kl.py

# CLI smoke check
python kl.py process examples/sample1.srt --mock -o exports_check
python kl.py process examples/sample2.txt --mock -o exports_check

# Skill layout validation
python tools/validate_skills.py --skills-dir skills
```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings for public functions

## Contributing Skills

When adding or updating skills under `skills/`:

1. Keep skill folder name in lowercase kebab-case.
2. Ensure `SKILL.md` has valid frontmatter (`name`, `description`).
3. Put prompt templates in `references/*.md` with:
   - `## Template` section
   - non-empty fenced template block
4. Keep `scripts/` directory present for orchestrated usage.
5. Run validation before opening PR:

```bash
python tools/validate_skills.py --skills-dir skills
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run local checks
5. Submit a pull request

## Report Issues

Please include:
- Python version
- Error message
- Steps to reproduce
