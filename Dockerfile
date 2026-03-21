FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY *.py ./

RUN pip install --no-cache-dir ".[all-ai]"

ENTRYPOINT ["python", "main.py"]
