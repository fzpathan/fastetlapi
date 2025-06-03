from flask import Flask, request, jsonify
from tasks.task_manager import init_globals, run_etl_task, get_task_status, get_task_output, stop_task

app = Flask(__name__)

@app.route("/run/<step_name>", methods=["POST"])
def run_step(step_name):
    params = request.get_json()
    return jsonify(run_etl_task(step_name, params))

@app.route("/status/<task_id>", methods=["GET"])
def status(task_id):
    return jsonify(get_task_status(task_id))

@app.route("/output/<task_id>", methods=["GET"])
def output(task_id):
    return jsonify(get_task_output(task_id))

@app.route("/stop/<task_id>", methods=["POST"])
def stop(task_id):
    return jsonify(stop_task(task_id))

if __name__ == "__main__":
    from tasks.task_manager import init_globals
    init_globals()
    app.run(debug=True)