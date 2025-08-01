"""
HTTP wrapper for customdoc MCP server with path prefix support
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
import argparse
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

# Create FastAPI app with root_path for ALB routing
app = FastAPI(
    title=f"customdoc MCP Server",
    root_path="/customdoc",
    docs_url="/customdoc/docs",
    redoc_url="/customdoc/redoc"
)

@app.get("/")
@app.get("/customdoc")
async def root():
    """Root endpoint info"""
    return {
        "service": "customdoc MCP Server",
        "status": "running",
        "prefix": "/customdoc",
        "endpoints": ["/customdoc/health", "/customdoc/tools", "/customdoc/call-tool"]
    }

@app.get("/health")
@app.get("/customdoc/health")
async def health_check():
    """Health check endpoint for ALB"""
    return {
        "status": "healthy", 
        "service": "customdoc-mcp",
        "timestamp": datetime.utcnow().isoformat(),
        "port": 8005
    }

@app.post("/call-tool")
@app.post("/customdoc/call-tool")
async def call_tool(request: MCPRequest) -> MCPResponse:
    """Call MCP tool via subprocess"""
    try:
        result = await execute_mcp_tool(request.tool, request.arguments)
        return MCPResponse(success=True, result=result)
    except Exception as e:
        logger.error(f"Error calling MCP tool {request.tool}: {str(e)}")
        return MCPResponse(success=False, error=str(e))

@app.get("/tools")
@app.get("/customdoc/tools")
async def list_tools():
    """List available MCP tools"""
    try:
        result = await execute_mcp_command("tools/list")
        return {"success": True, "tools": result}
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        return {"success": False, "error": str(e)}

async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute MCP tool via subprocess"""
    try:
        # Get the MCP command based on service
        mcp_commands = {
            "core": ["python", "-m", "awslabscore_mcp_server"],
            "pricing": ["python", "-m", "awslabspricing_mcp_server"], 
            "awsdocs": ["python", "-m", "awslabsaws_documentation_mcp_server"],
            "cfn": ["python", "-m", "awslabscloudformation_mcp_server"],
            "diagram": ["awslabs.aws-diagram-mcp-server"],
            "customdoc": ["python", "document_generator_mcp.py"]
        }
        
        cmd = mcp_commands.get("customdoc", ["echo", "unknown"])
        
        # Prepare input for MCP server
        mcp_input = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(
            input=json.dumps(mcp_input).encode()
        )
        
        if process.returncode != 0:
            raise Exception(f"MCP command failed: {stderr.decode()}")
        
        # Parse response
        response = json.loads(stdout.decode())
        
        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")
        
        return response.get("result", {})
        
    except Exception as e:
        logger.error(f"Error executing MCP tool: {str(e)}")
        raise

async def execute_mcp_command(method: str, params: Optional[Dict] = None) -> Any:
    """Execute generic MCP command"""
    try:
        # Get the MCP command based on service
        mcp_commands = {
            "core": ["python", "-m", "awslabscore_mcp_server"],
            "pricing": ["python", "-m", "awslabspricing_mcp_server"], 
            "awsdocs": ["python", "-m", "awslabsaws_documentation_mcp_server"],
            "cfn": ["python", "-m", "awslabscloudformation_mcp_server"],
            "diagram": ["awslabs.aws-diagram-mcp-server"],
            "customdoc": ["python", "document_generator_mcp.py"]
        }
        
        cmd = mcp_commands.get("customdoc", ["echo", "unknown"])
        
        mcp_input = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(
            input=json.dumps(mcp_input).encode()
        )
        
        if process.returncode != 0:
            raise Exception(f"MCP command failed: {stderr.decode()}")
        
        response = json.loads(stdout.decode())
        
        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")
        
        return response.get("result", {})
        
    except Exception as e:
        logger.error(f"Error executing MCP command: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
