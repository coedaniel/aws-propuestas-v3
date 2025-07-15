FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install the official AWS Labs core MCP server
RUN uv tool install awslabs.core-mcp-server@latest

# Create a simple HTTP wrapper to expose MCP over HTTP with path prefix support
COPY mcp_http_wrapper_core.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Health check - now works with path prefix
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "mcp_http_wrapper_core.py"]
