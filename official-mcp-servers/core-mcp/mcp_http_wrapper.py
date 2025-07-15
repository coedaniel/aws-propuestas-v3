"""
Generic HTTP wrapper for AWS Labs MCP servers
Exposes MCP servers over HTTP for ECS deployment
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
import argparse

from fastapi import FastAPI, HTTPException
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

class MCPHttpWrapper:
    def __init__(self, mcp_command: str, mcp_args: List[str], port: int = 8000):
        self.mcp_command = mcp_command
        self.mcp_args = mcp_args
        self.port = port
        self.app = FastAPI(title=f"MCP HTTP Wrapper - {mcp_args[0] if mcp_args else 'Unknown'}")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy", 
                "service": f"mcp-wrapper-{self.mcp_args[0] if self.mcp_args else 'unknown'}",
                "port": self.port
            }
        
        @self.app.post("/call-tool")
        async def call_tool(request: MCPRequest) -> MCPResponse:
            """Call MCP tool via subprocess"""
            try:
                result = await self.execute_mcp_tool(request.tool, request.arguments)
                return MCPResponse(success=True, result=result)
            except Exception as e:
                logger.error(f"Error calling MCP tool {request.tool}: {str(e)}")
                return MCPResponse(success=False, error=str(e))
        
        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools"""
            try:
                result = await self.execute_mcp_command("list_tools")
                return {"success": True, "tools": result}
            except Exception as e:
                logger.error(f"Error listing tools: {str(e)}")
                return {"success": False, "error": str(e)}
    
    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute MCP tool via subprocess"""
        try:
            # Prepare the command
            cmd = [self.mcp_command] + self.mcp_args
            
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
    
    async def execute_mcp_command(self, method: str, params: Optional[Dict] = None) -> Any:
        """Execute generic MCP command"""
        try:
            cmd = [self.mcp_command] + self.mcp_args
            
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
    
    async def run(self):
        """Run the HTTP wrapper server"""
        config = uvicorn.Config(
            self.app, 
            host="0.0.0.0", 
            port=self.port, 
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP HTTP Wrapper")
    parser.add_argument("--port", type=int, default=8000, help="Port to run HTTP server on")
    parser.add_argument("--mcp-command", required=True, help="MCP command to execute")
    parser.add_argument("--mcp-args", required=True, help="MCP command arguments")
    
    args = parser.parse_args()
    
    # Parse MCP args (could be comma-separated or space-separated)
    mcp_args = args.mcp_args.split() if ' ' in args.mcp_args else [args.mcp_args]
    
    wrapper = MCPHttpWrapper(
        mcp_command=args.mcp_command,
        mcp_args=mcp_args,
        port=args.port
    )
    
    logger.info(f"Starting MCP HTTP Wrapper on port {args.port}")
    logger.info(f"MCP Command: {args.mcp_command} {' '.join(mcp_args)}")
    
    asyncio.run(wrapper.run())

if __name__ == "__main__":
    main()
