from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from tasks.task_manager import init_globals, run_etl_task, get_task_status, get_task_output, stop_task
import uvicorn

app = FastAPI(title="ETL API", description="API for running ETL tasks", version="1.0.0")

# Pydantic models for request/response validation
class RunStepRequest(BaseModel):
    params: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    pid: int

class StatusResponse(BaseModel):
    status: str
    output: Optional[Any] = None

class OutputResponse(BaseModel):
    output: Any

class StopResponse(BaseModel):
    status: str
    task_id: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize globals when the application starts"""
    init_globals()

@app.post("/run/{step_name}", response_model=TaskResponse)
async def run_step(step_name: str, request: RunStepRequest):
    """Run an ETL step with given parameters"""
    try:
        result = run_etl_task(step_name, request.params)
        return TaskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    """Get the status of a running task"""
    try:
        result = get_task_status(task_id)
        return StatusResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/output/{task_id}")
async def get_output(task_id: str):
    """Get the output of a task"""
    try:
        result = get_task_output(task_id)
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop/{task_id}", response_model=StopResponse)
async def stop_task_endpoint(task_id: str):
    """Stop a running task"""
    try:
        result = stop_task(task_id)
        return StopResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    init_globals()
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
