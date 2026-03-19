# Contributing to Rattle API

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/rattle-api.git
   cd rattle-api
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API key:
   ```bash
   cp .env.example .env
   ```
5. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

- Follow existing code patterns and conventions
- Keep functions focused and well-named
- Add docstrings for public functions
- Use type hints where they improve clarity

## Pull Request Guidelines

- One feature or fix per pull request
- Use a descriptive title that summarizes the change
- Include a brief description of what changed and why
- Test your changes before submitting

## Reporting Issues

- Use the GitHub issue templates for bug reports and feature requests
- Include steps to reproduce for bugs
- Include your Python version and OS

## Content and Examples

- Example scripts go in `examples/`
- Keep examples generic and reusable (no tenant-specific data)
- Document any new API endpoints or patterns you discover

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
