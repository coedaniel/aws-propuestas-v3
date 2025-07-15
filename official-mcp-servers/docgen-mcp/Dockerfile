FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Node.js for repomix
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install repomix (required by code-doc-gen-mcp-server)
RUN pip install repomix>=0.2.6

# Install the official AWS Labs documentation MCP server (not code-doc-gen)
RUN uv tool install awslabs.aws-documentation-mcp-server@latest

# Create a simple HTTP wrapper to expose MCP over HTTP
COPY mcp_http_wrapper_awsdocs.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["python", "mcp_http_wrapper_awsdocs.py"]
