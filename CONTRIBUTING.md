# Contributing to rattleGRIMOIRE

Thank you for offering your craft to the Grimoire. Every new spell makes
the codex stronger. This guide will help you begin the ritual.

## Joining the Coven

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/rattleGRIMOIRE.git
   cd rattleGRIMOIRE
   ```
3. **Open a new chapter** for your change:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Bind** development dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev,all-ai,all-sources]"
   ```

## Development Rites

### Running the rites

```bash
make lint     # Ruff — banish formatting demons
make test     # pytest — 170+ tests · ~97% coverage
make check    # All rites, in sequence
make format   # Auto-purify with Ruff
```

### Code style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Line length: 100 characters.
- Target Python version: 3.10+.
- Configuration lives in `pyproject.toml` under `[tool.ruff]`.

### Commit messages

Inscribe clear, concise commit messages:

- Use the imperative mood: "Add feature" not "Added feature".
- Keep the first line under 72 characters.
- Reference issues where relevant: `Fix #42`.

### Pull requests

1. Ensure all rites pass (`make check`).
2. Update documentation if your change affects user-facing behaviour.
3. Add a changelog entry under `[Unreleased]` in `CHANGELOG.md`.
4. Keep pull requests focused — one spell or fix per PR.
5. Fill out the pull request template.

## Adding a New AI Sigil (Provider)

1. Create a new class in `rattle_api/provider.py` that extends `AIProvider`.
2. Implement the `complete()` method.
3. Register it in the `PROVIDERS` dict.
4. Document required environment runes in `rattle_api/config.py` and `.env.example`.
5. Add the sigil to the table in `README.md`.

## Adding a New Spell (CLI Command)

1. Add a handler function `cmd_your_command(tenant, args)` in `rattle_api/main.py`.
2. Add a subparser inside `main()`.
3. Register it in the `commands` dispatch dict.
4. Add tests in `tests/test_main.py`.
5. Document the spell in `README.md` and `SETUP.md`.

## Reporting Omens (Issues)

- Use the [GitHub issue tracker](https://github.com/mngapps/rattleGRIMOIRE/issues).
- Check existing issues before creating a new one.
- Include steps to reproduce, expected behaviour, and actual behaviour.
- For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold it.

---

*May your agents forever cast true.*
