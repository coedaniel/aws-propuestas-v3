# src/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from .generator import generate_all
import json

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "document-generator-mcp"}

class DocRequest(BaseModel):
    project_name: str
    description: str

@app.post("/generate")
def generate(req: DocRequest):
    result = generate_all(req.project_name, req.description)
    return {"result": result}

# MCP compatible endpoints
@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name": "generate_document",
                "description": "Generate documentation files (DOCX, TXT, CSV) for a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        }
                    },
                    "required": ["project_name", "description"]
                }
            }
        ]
    }

@app.post("/call-tool")
async def call_tool(request: Request):
    try:
        data = await request.json()
        
        if data.get("name") == "generate_document":
            params = data.get("parameters", {})
            project_name = params.get("project_name", "")
            description = params.get("description", "")
            
            if not project_name or not description:
                return {"error": "Missing required parameters", "success": False}
            
            result = generate_all(project_name, description)
            return {"result": result, "success": True}
        else:
            return {"error": f"Unknown tool: {data.get('name')}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
