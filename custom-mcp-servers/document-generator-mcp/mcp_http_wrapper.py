#!/usr/bin/env python3
"""
HTTP wrapper for Custom Document Generator MCP Server
Exposes document generation functionality over HTTP for ECS deployment
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import argparse
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import uvicorn

# Import our custom MCP server
from document_generator_mcp import MCP_TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Generator MCP HTTP Wrapper")

class DocumentRequest(BaseModel):
    content: Dict[str, Any]

class ExcelRequest(BaseModel):
    data: Dict[str, Any]

class ProposalRequest(BaseModel):
    template_type: str
    variables: Dict[str, Any]

class S3UploadRequest(BaseModel):
    filepath: str
    bucket: str
    key: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document-generator-mcp"}

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": list(MCP_TOOLS.keys()),
        "description": "Custom Document Generator MCP Server - Generate Word docs, Excel reports, and proposals"
    }

@app.post("/generate/word")
async def generate_word_document(request: DocumentRequest):
    """Generate a Word document"""
    try:
        result = await MCP_TOOLS['generate_word_document'](request.content)
        return result
    except Exception as e:
        logger.error(f"Error generating Word document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/excel")
async def generate_excel_report(request: ExcelRequest):
    """Generate an Excel report"""
    try:
        result = await MCP_TOOLS['generate_excel_report'](request.data)
        return result
    except Exception as e:
        logger.error(f"Error generating Excel report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/proposal")
async def generate_proposal_template(request: ProposalRequest):
    """Generate a proposal document from template"""
    try:
        result = await MCP_TOOLS['generate_proposal_template'](
            request.template_type, 
            request.variables
        )
        return result
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/s3")
async def upload_to_s3(request: S3UploadRequest):
    """Upload document to S3"""
    try:
        result = await MCP_TOOLS['upload_to_s3'](
            request.filepath,
            request.bucket,
            request.key
        )
        return result
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_generated_documents():
    """List all generated documents"""
    try:
        result = await MCP_TOOLS['list_generated_documents']()
        return result
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Dict[str, Any]):
    """Generic tool calling endpoint"""
    try:
        if tool_name not in MCP_TOOLS:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        tool_function = MCP_TOOLS[tool_name]
        
        # Handle different tool signatures
        if tool_name == 'generate_word_document':
            result = await tool_function(request.get('content', {}))
        elif tool_name == 'generate_excel_report':
            result = await tool_function(request.get('data', {}))
        elif tool_name == 'generate_proposal_template':
            result = await tool_function(
                request.get('template_type', 'basic'),
                request.get('variables', {})
            )
        elif tool_name == 'upload_to_s3':
            result = await tool_function(
                request.get('filepath', ''),
                request.get('bucket', ''),
                request.get('key', '')
            )
        elif tool_name == 'list_generated_documents':
            result = await tool_function()
        else:
            result = await tool_function(**request)
        
        return result
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template examples endpoint
@app.get("/templates")
async def get_template_info():
    """Get information about available templates"""
    return {
        "templates": {
            "basic": {
                "description": "Basic AWS proposal template",
                "required_variables": [
                    "client_name", "date", "prepared_by", "primary_services",
                    "business_objectives", "aws_services_list", "timeline",
                    "duration", "estimated_cost"
                ]
            },
            "detailed": {
                "description": "Comprehensive AWS architecture proposal",
                "required_variables": [
                    "client_name", "date", "prepared_by", "project_code",
                    "executive_summary", "current_state", "proposed_architecture",
                    "compute_services", "storage_solutions", "networking",
                    "security", "implementation_plan", "cost_analysis", "risk_assessment"
                ]
            },
            "executive": {
                "description": "Executive summary brief",
                "required_variables": [
                    "client_name", "date", "prepared_by", "executive_sponsor",
                    "business_case", "strategic_benefits", "benefits_list",
                    "investment_overview", "next_steps"
                ]
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Document Generator MCP HTTP Wrapper")
    parser.add_argument("--port", type=int, default=8005, help="Port to run on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Document Generator MCP HTTP wrapper on {args.host}:{args.port}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
