from fastapi import FastAPI, Request
from tasks.task_manager import run_etl_task, get_task_status, get_task_output, stop_task

app = FastAPI()

@app.post("/run/{step_name}")
def run_step(step_name: str, request: Request):
    params = request.json()
    return run_etl_task(step_name, params)

@app.get("/status/{task_id}")
def status(task_id: str):
    return get_task_status(task_id)

@app.get("/output/{task_id}")
def output(task_id: str):
    return get_task_output(task_id)

@app.post("/stop/{task_id}")
def stop(task_id: str):
    return stop_task(task_id)