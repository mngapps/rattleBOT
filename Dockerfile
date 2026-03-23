FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY rattle_api/ rattle_api/

RUN pip install --no-cache-dir ".[all-ai]"

ENTRYPOINT ["rattle"]
