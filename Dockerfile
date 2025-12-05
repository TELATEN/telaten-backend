# Builder stage: install deps and build wheel/cache
FROM python:3.12-alpine AS builder

# Install build deps
RUN apk add --no-cache build-base linux-headers libffi-dev openssl-dev \
  && python -m ensurepip

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-install-project

# Final stage: runtime
FROM python:3.12-alpine

# Install Node.js and npm (provides npx) for MCP servers
RUN apk add --no-cache nodejs npm

# create non-root user
RUN adduser -D appuser
WORKDIR /app

# copy installed site-packages from builder - using pip wheel cache isn't straightforward on alpine, so copy project and rely on installed deps
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# copy app
COPY --chown=appuser:appuser . .

# ensure virtualenv dir is writable and fix ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8065
CMD ["uv", "run", "python", "run.py"]
