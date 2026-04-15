# Security Policy — rattleGRIMOIRE

A Grimoire is only as safe as its bindings. Report weaknesses responsibly.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email the maintainers directly or use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-managing-vulnerabilities/privately-reporting-a-security-vulnerability).

### What to include

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response timeline

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 1 week
- **Fix or mitigation**: as soon as practical, targeting 30 days

## Security Best Practices for Users

- Never commit your `.env` file or API keys to version control.
- Use environment variables or a secrets manager for credentials.
- When running with `--push`, review AI-generated data before it reaches production.
- Keep dependencies up to date (`pip install --upgrade`).
