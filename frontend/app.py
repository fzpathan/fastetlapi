import streamlit as st
import requests
import json

BASE_URL = "http://localhost:8000"

st.title("ETL Process Tester")

step = st.selectbox("Choose ETL Step", ["extract", "transform", "load"])
params = st.text_area("Parameters (JSON)", "{}")

if st.button("Run"):
    response = requests.post(f"{BASE_URL}/run/{step}", json=json.loads(params))
    st.session_state.task_id = response.json()['task_id']
    st.success(f"Started {step} task with ID: {st.session_state.task_id}")

if "task_id" in st.session_state:
    if st.button("Check Status"):
        status = requests.get(f"{BASE_URL}/status/{st.session_state.task_id}").json()
        st.write("Status:", status)

    if st.button("Get Output"):
        output = requests.get(f"{BASE_URL}/output/{st.session_state.task_id}").json()
        st.json(output)

    if st.button("Stop Task"):
        stop = requests.post(f"{BASE_URL}/stop/{st.session_state.task_id}").json()
        st.warning(f"Stopped: {stop}")