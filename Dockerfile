FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY srl .
COPY pyproject.toml uv.lock ./

ENV UV_NO_DEV=1
RUN uv sync --locked

EXPOSE 8080

CMD ["srl", "server", "--host", "0.0.0.0", "--port", "8080"]
