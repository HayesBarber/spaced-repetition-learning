FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .
COPY srl .

ENV UV_SYSTEM_PYTHON=1
ENV UV_NO_DEV=1

RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["srl", "server", "--host", "0.0.0.0", "--port", "8080"]
