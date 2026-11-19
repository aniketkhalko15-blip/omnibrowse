import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Pocket Agent OS", description="Mobile Terminal & File System Engine")

WORKSPACE_DIR = os.path.abspath("./workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class CommandRequest(BaseModel):
    command: str

class FileWriteRequest(BaseModel):
    path: str
    content: str

class FileReadRequest(BaseModel):
    path: str

@app.get("/")
def home():
    return {
        "status": "online",
        "system": "Pocket Agent OS",
        "workspace": WORKSPACE_DIR
    }

@app.post("/terminal/run")
def run_command(req: CommandRequest):
    """Executes bash/powershell commands inside the workspace."""
    try:
        result = subprocess.run(
            req.command,
            shell=True,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out (30s limit)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fs/write")
def write_file(req: FileWriteRequest):
    """Creates or overwrites a code/text file."""
    try:
        full_path = os.path.abspath(os.path.join(WORKSPACE_DIR, req.path))
        if not full_path.startswith(WORKSPACE_DIR):
            raise HTTPException(status_code=403, detail="Path outside workspace forbidden")
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(req.content)
            
        return {"status": "success", "file": req.path, "bytes": len(req.content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fs/read")
def read_file(req: FileReadRequest):
    """Reads file content."""
    try:
        full_path = os.path.abspath(os.path.join(WORKSPACE_DIR, req.path))
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fs/list")
def list_files():
    """Lists files in the project workspace."""
    files = []
    for root, _, filenames in os.walk(WORKSPACE_DIR):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), WORKSPACE_DIR)
            files.append(rel)
    return {"workspace_files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)
