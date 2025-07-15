#!/bin/bash

# Setup Local Code Documentation Generation MCP Server
# This script sets up the AWS Labs code-doc-gen-mcp-server locally

set -e

echo "🚀 Setting up AWS Labs Code Documentation Generation MCP Server locally..."

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Install repomix (required dependency)
echo "📦 Installing repomix..."
if ! command -v repomix &> /dev/null; then
    npm install -g repomix
fi

# Install the code-doc-gen MCP server
echo "📦 Installing AWS Labs code-doc-gen-mcp-server..."
uv tool install awslabs.code-doc-gen-mcp-server@latest

# Verify installation
echo "✅ Verifying installation..."
if uv tool list | grep -q "code-doc-gen-mcp-server"; then
    echo "✅ code-doc-gen-mcp-server installed successfully!"
else
    echo "❌ Installation failed!"
    exit 1
fi

echo ""
echo "🎯 Setup complete! You can now use the code documentation generator."
echo ""
echo "📋 Usage examples:"
echo "1. Generate documentation for current repository:"
echo "   uvx awslabs.code-doc-gen-mcp-server@latest"
echo ""
echo "2. Or use it with MCP client integration"
echo ""
echo "🔧 The server provides these tools:"
echo "- prepare_repository: Extract directory structure and analyze project"
echo "- create_context: Create documentation context from analysis"
echo "- plan_documentation: Create documentation plan"
echo "- generate_documentation: Generate actual documentation content"
echo ""
echo "💡 Perfect for cleaning up your messy repository with proper documentation!"
