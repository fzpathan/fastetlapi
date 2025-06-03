import uuid
import multiprocessing
from etl import extract, transform, load

etl_map = {
    "extract": extract.run,
    "transform": transform.run,
    "load": load.run
}

task_registry = {}
manager = None
shared_output = None

def init_globals():
    global manager, shared_output
    manager = multiprocessing.Manager()
    shared_output = manager.dict()

def etl_worker(task_id, step_name, params, shared_output):
    try:
        result = etl_map[step_name](params)
        shared_output[task_id] = {"status": "completed", "output": result}
    except Exception as e:
        shared_output[task_id] = {"status": "failed", "output": str(e)}

def run_etl_task(step_name, params):
    task_id = str(uuid.uuid4())
    shared_output[task_id] = {"status": "running", "output": None}
    p = multiprocessing.Process(target=etl_worker, args=(task_id, step_name, params, shared_output))
    p.start()
    task_registry[task_id] = {"process": p, "pid": p.pid}
    return {"task_id": task_id, "status": "started", "pid": p.pid}

def get_task_status(task_id):
    if task_id not in task_registry:
        return {"status": "not_found"}
    if shared_output[task_id]["status"] == "running":
        p = task_registry[task_id]["process"]
        if not p.is_alive():
            shared_output[task_id]["status"] = "unknown"
    return shared_output.get(task_id, {"status": "unknown"})

def get_task_output(task_id):
    return shared_output.get(task_id, {}).get("output", "No output yet.")

def stop_task(task_id):
    task_info = task_registry.get(task_id)
    if not task_info:
        return {"status": "not_found"}
    process = task_info["process"]
    if process.is_alive():
        process.terminate()
        process.join()
        shared_output[task_id] = {"status": "terminated", "output": None}
        return {"status": "terminated", "task_id": task_id}
    return {"status": "not_running"}