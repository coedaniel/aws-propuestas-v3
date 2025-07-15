#!/bin/bash

# Script to update all Dockerfiles with new wrappers
set -e

echo "🐳 Updating Dockerfiles for all MCP services..."

# Define services
SERVICES=("core" "pricing" "awsdocs" "cfn" "diagram")

for service in "${SERVICES[@]}"; do
    echo "📝 Updating ${service}-mcp Dockerfile..."
    
    # Copy the service-specific wrapper
    cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_${service}.py" \
       "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/${service}-mcp/"
    
    # Update the Dockerfile CMD line
    sed -i "s/mcp_http_wrapper.py/mcp_http_wrapper_${service}.py/g" \
        "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/${service}-mcp/Dockerfile"
    
    # Update the CMD to just run the Python file directly
    sed -i 's/CMD \["python", "mcp_http_wrapper_.*\.py", .*\]/CMD ["python", "mcp_http_wrapper_'${service}'.py"]/g' \
        "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/${service}-mcp/Dockerfile"
    
    echo "✅ Updated ${service}-mcp"
done

# Handle custom doc service separately
echo "📝 Updating customdoc-mcp..."
cp "/home/ec2-user/aws-propuestas-v3/official-mcp-servers/mcp_http_wrapper_customdoc.py" \
   "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/"

# Update custom doc Dockerfile
sed -i 's/COPY mcp_http_wrapper.py ./COPY mcp_http_wrapper_customdoc.py ./' \
    "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/Dockerfile"

sed -i 's/CMD \["python", "mcp_http_wrapper.py"\]/CMD ["python", "mcp_http_wrapper_customdoc.py"]/' \
    "/home/ec2-user/aws-propuestas-v3/custom-mcp-servers/document-generator-mcp/Dockerfile"

echo "✅ Updated customdoc-mcp"

echo "🎉 All Dockerfiles updated!"
echo ""
echo "📋 Ready to rebuild Docker images!"
