#!/bin/bash

# Script to update all Dockerfiles with new wrappers
set -e

echo "🐳 Updating Dockerfiles for all MCP services..."

# Copy wrappers to their respective directories
echo "📝 Copying wrappers..."

cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_pricing.py" \
   "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/pricing-mcp/"

cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_awsdocs.py" \
   "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/docgen-mcp/"

cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_cfn.py" \
   "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/cfn-mcp/"

cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_diagram.py" \
   "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/diagram-mcp/"

cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_customdoc.py" \
   "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/"

echo "✅ All wrappers copied"

# Update Dockerfiles
echo "📝 Updating Dockerfiles..."

# Update pricing-mcp
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_pricing.py ./' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/pricing-mcp/Dockerfile"
sed -i 's/CMD \["python", "mcp_http_wrapper.py".*\]/CMD ["python", "mcp_http_wrapper_pricing.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/pricing-mcp/Dockerfile"

# Update docgen-mcp (AWS Docs)
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_awsdocs.py ./' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/docgen-mcp/Dockerfile"
sed -i 's/CMD \["python", "mcp_http_wrapper.py".*\]/CMD ["python", "mcp_http_wrapper_awsdocs.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/docgen-mcp/Dockerfile"

# Update cfn-mcp
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_cfn.py ./' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/cfn-mcp/Dockerfile"
sed -i 's/CMD \["python", "mcp_http_wrapper.py".*\]/CMD ["python", "mcp_http_wrapper_cfn.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/cfn-mcp/Dockerfile"

# Update diagram-mcp
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_diagram.py ./' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/diagram-mcp/Dockerfile"
sed -i 's/CMD \["python", "mcp_http_wrapper.py".*\]/CMD ["python", "mcp_http_wrapper_diagram.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/diagram-mcp/Dockerfile"

# Update custom doc service
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_customdoc.py ./' \
    "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/Dockerfile"
sed -i 's/CMD \["python", "mcp_http_wrapper.py"\]/CMD ["python", "mcp_http_wrapper_customdoc.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/Dockerfile"

echo "✅ All Dockerfiles updated"

echo "🎉 Ready to rebuild Docker images!"
echo ""
echo "📋 Next: Run the build script to rebuild all images"
