import streamlit as st
import requests
import os
import pandas as pd

API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")

st.set_page_config(page_title="KOMBAJN Dashboard", layout="wide")
st.title("📊 Celery Queue Monitor")

def fetch_tasks():
    try:
        resp = requests.get(f"{API_BASE}/tasks/list", timeout=5)
        return resp.json().get("tasks", [])
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        return []

if st.button("🔄 Refresh Queue"):
    tasks = fetch_tasks()
    if tasks:
        df = pd.DataFrame(tasks)
        st.table(df)
    else:
        st.info("No active or queued tasks.")
