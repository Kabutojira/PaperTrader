# Hermes skills

Each immediate child directory is a Hermes skill and must contain a `SKILL.md` file with valid frontmatter.

This repository intentionally uses the capitalized directory name `Skills`. Configure Hermes with the exact path:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/PaperTrader/Skills
```

Current skills:

- `papertrader` — orchestrates the Google Sheets trading registry while preserving deterministic risk and execution boundaries.

Skill-local supporting files belong in:

- `references/` for detailed operating contracts;
- `templates/` for schemas and examples;
- `scripts/` for deterministic helpers used by the skill;
- `assets/` for non-code supplementary files, when needed.
