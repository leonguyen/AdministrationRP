# TailAdmin (AdministrationRP) — production image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Install dependencies first (better layer caching) using the committed lockfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the application source.
COPY main.py ./
COPY app ./app
COPY assets ./assets

# Render supplies $PORT; default for local `docker run`.
ENV PORT=8080
EXPOSE 8080

# Put the virtualenv's bin on PATH so `python` resolves to the synced interpreter.
ENV PATH="/app/.venv/bin:$PATH"

# Non-root user.
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

# Persist the SQLite DB on a mounted volume if available.
ENV TAILADMIN_DB=/app/data/tailadmin.db

CMD ["python", "main.py"]