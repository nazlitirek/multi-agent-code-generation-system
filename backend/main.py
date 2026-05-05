from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.planner import chat_with_planner
from agents.architect import generate_architecture
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/planner/chat")
async def planner_chat(req: ChatRequest):
    try:
        result = chat_with_planner(req.message, req.history)
        return result
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})



class ArchitectRequest(BaseModel):
    brief: str

@app.post("/architect/generate")
async def architect_generate(req: ArchitectRequest):
    try:
        result = generate_architecture(req.brief)
        return result
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
def health():
    return {"status": "ok"}


from agents.api_contract import generate_api_contract

class ApiContractRequest(BaseModel):
    architecture: dict

@app.post("/api-contract/generate")
async def api_contract_generate(req: ApiContractRequest):
    try:
        result = generate_api_contract(req.architecture)
        return result
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})
    

from fastapi.responses import FileResponse
from utils.file_writer import zip_project, list_files

@app.get("/project/{project_name}/files")
def get_project_files(project_name: str):
    files = list_files(project_name)
    return {"files": files}

@app.get("/project/{project_name}/download")
def download_project(project_name: str):
    zip_path = zip_project(project_name)
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{project_name}.zip"
    )