from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import pathlib
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-script")
async def run_script(request: Request):
    data = await request.json()
    option = data.get("option")
    value = data.get("value")
    mergePdfs = data.get("mergePdfs", False)
    examFilter = data.get("examFilter", "all")
    script_path = pathlib.Path("../exam-parser/tiet_papers_downloader.py").resolve()
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        cmd = ["python", str(script_path), str(option), str(value), str(mergePdfs), str(examFilter)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        output = result.stdout
        error = result.stderr
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"output": output, "error": error})

@app.get("/")
def root():
    return {"status": "Backend running"}
