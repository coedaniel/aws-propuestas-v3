#!/usr/bin/env python3
"""
HTTP wrapper for AWS Documentation MCP Server
Exposes MCP functionality over HTTP for ECS deployment
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any, List, Optional
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AWS Documentation MCP HTTP Wrapper")

class MCPRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPClient:
    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args
        self.process = None
        
    async def start(self):
        """Start the MCP server process"""
        try:
            cmd = [self.command] + self.args
            logger.info(f"Starting MCP server: {' '.join(cmd)}")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize MCP connection
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "http-wrapper",
                        "version": "1.0.0"
                    }
                }
            }
            
            await self._send_request(init_request)
            logger.info("MCP server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response
            response_line = await self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from MCP server")
            
            response = json.loads(response_line.decode().strip())
            return response
            
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        return await self._send_request(request)
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }
        
        return await self._send_request(request)
    
    async def stop(self):
        """Stop the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Global MCP client instance
mcp_client: Optional[MCPClient] = None

@app.on_event("startup")
async def startup_event():
    global mcp_client
    # MCP client will be initialized when first request comes in
    pass

@app.on_event("shutdown")
async def shutdown_event():
    global mcp_client
    if mcp_client:
        await mcp_client.stop()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "aws-documentation-mcp"}

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    global mcp_client
    
    if not mcp_client:
        return {"error": "MCP client not initialized"}
    
    try:
        response = await mcp_client.list_tools()
        return response
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Dict[str, Any]):
    """Call a specific MCP tool"""
    global mcp_client
    
    if not mcp_client:
        return {"error": "MCP client not initialized"}
    
    try:
        response = await mcp_client.call_tool(tool_name, request)
        return response
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documentation(request: Dict[str, Any]):
    """Search AWS documentation"""
    global mcp_client
    
    if not mcp_client:
        # Initialize MCP client on first request
        mcp_client = MCPClient("uvx", ["awslabs.aws-documentation-mcp-server@latest"])
        await mcp_client.start()
    
    try:
        search_phrase = request.get("search_phrase", "")
        limit = request.get("limit", 10)
        
        response = await mcp_client.call_tool("search_documentation", {
            "search_phrase": search_phrase,
            "limit": limit
        })
        return response
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/read")
async def read_documentation(request: Dict[str, Any]):
    """Read AWS documentation page"""
    global mcp_client
    
    if not mcp_client:
        # Initialize MCP client on first request
        mcp_client = MCPClient("uvx", ["awslabs.aws-documentation-mcp-server@latest"])
        await mcp_client.start()
    
    try:
        url = request.get("url", "")
        max_length = request.get("max_length", 5000)
        start_index = request.get("start_index", 0)
        
        response = await mcp_client.call_tool("read_documentation", {
            "url": url,
            "max_length": max_length,
            "start_index": start_index
        })
        return response
    except Exception as e:
        logger.error(f"Error reading documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend")
async def recommend_documentation(request: Dict[str, Any]):
    """Get documentation recommendations"""
    global mcp_client
    
    if not mcp_client:
        # Initialize MCP client on first request
        mcp_client = MCPClient("uvx", ["awslabs.aws-documentation-mcp-server@latest"])
        await mcp_client.start()
    
    try:
        url = request.get("url", "")
        
        response = await mcp_client.call_tool("recommend", {
            "url": url
        })
        return response
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    parser = argparse.ArgumentParser(description="AWS Documentation MCP HTTP Wrapper")
    parser.add_argument("--port", type=int, default=8002, help="Port to run on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--mcp-command", default="uvx", help="MCP server command")
    parser.add_argument("--mcp-args", nargs="+", default=["awslabs.aws-documentation-mcp-server@latest"], help="MCP server arguments")
    
    args = parser.parse_args()
    
    logger.info(f"Starting AWS Documentation MCP HTTP wrapper on {args.host}:{args.port}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
