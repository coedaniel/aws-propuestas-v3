"""
HTTP wrapper for core MCP server with CORS support
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
import argparse
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
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

# Create FastAPI app
app = FastAPI(
    title="core MCP Server",
    description="HTTP wrapper for core MCP server with CORS support"
)

# CORS configuration - MUST be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://main.d2xsphsjdxlk24.amplifyapp.com",
        "https://d2xsphsjdxlk24.amplifyapp.com",
        "http://localhost:3000",  # For development
        "http://localhost:8080"   # For development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for ALB"""
    return {
        "status": "healthy", 
        "service": "core-mcp",
        "timestamp": datetime.utcnow().isoformat(),
        "port": 8000,
        "cors_enabled": True
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint info"""
    return {
        "service": "core MCP Server",
        "status": "running",
        "endpoints": ["/health", "/tools", "/call-tool"],
        "cors_enabled": True
    }

# Manual CORS preflight handler as fallback
@app.options("/{path:path}")
async def options_preflight(path: str, request: Request):
    """Handle CORS preflight requests manually"""
    origin = request.headers.get("origin")
    
    # Check if origin is allowed
    allowed_origins = [
        "https://main.d2xsphsjdxlk24.amplifyapp.com",
        "https://d2xsphsjdxlk24.amplifyapp.com",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    if origin in allowed_origins:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
        return Response(status_code=200, headers=headers)
    
    return Response(status_code=403)

@app.post("/call-tool")
async def call_tool(request: MCPRequest) -> MCPResponse:
    """Call MCP tool via subprocess"""
    try:
        result = await execute_mcp_tool(request.tool, request.arguments)
        return MCPResponse(success=True, result=result)
    except Exception as e:
        logger.error(f"Error calling MCP tool {request.tool}: {str(e)}")
        return MCPResponse(success=False, error=str(e))

@app.get("/tools")
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
        cmd = ["python", "-m", "awslabscore_mcp_server"]
        
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
        cmd = ["python", "-m", "awslabscore_mcp_server"]
        
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
