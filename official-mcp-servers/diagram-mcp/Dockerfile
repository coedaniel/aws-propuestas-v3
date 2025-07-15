FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Graphviz for diagrams
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install the official AWS Labs diagram MCP server
RUN uv tool install awslabs.aws-diagram-mcp-server@latest

# Create a simple HTTP wrapper to expose MCP over HTTP
COPY mcp_http_wrapper_diagram.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

CMD ["python", "mcp_http_wrapper_diagram.py"]
