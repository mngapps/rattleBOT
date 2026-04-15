# Changelog — rattleGRIMOIRE

All notable changes to this Grimoire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Rebranded **Rattle AI Workspace** to **rattleGRIMOIRE** — the arcane spellbook
  of AI-powered product-data consulting. All user-facing documentation, CLI
  help text, package metadata, and repository URLs updated to reflect the new
  identity. The importable Python package remains `rattle_api` for historical
  compatibility with the Rattle REST API wrapper; the distribution is now
  published as `rattle-grimoire`.

## [0.1.0] - 2026-03-21

### Added

- Initial public release.
- AI-agnostic provider abstraction supporting OpenAI, Anthropic, Ollama, and custom HTTP endpoints.
- CLI commands: `test-connection`, `list-sources`, `ai-describe`, `ai-classify`, `ai-transform`, `ai-analyse`, `ai-providers`.
- Data interchange transformation between formats (Datanorm, eCl@ss, BMEcat, Rattle).
- Image processing utilities for product data.
- Comprehensive documentation, contributing guide, and CI pipeline.
