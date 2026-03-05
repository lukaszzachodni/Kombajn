import os
import json
from typing import Any, Dict

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.schemas import DatetimeToTimestampRequest, VideoEditManifest


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")


def _post_api(endpoint: str, payload: Any) -> Dict[str, Any]:
    """Common helper to push data to the API."""
    json_data = payload.model_dump() if hasattr(payload, "model_dump") else payload
    
    resp = requests.post(
        f"{API_BASE}{endpoint}",
        json=json_data,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _get_task(task_id: str) -> Dict[str, Any]:
    resp = requests.get(f"{API_BASE}/tasks/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    st.set_page_config(
        page_title="KOMBAJN · Control Panel",
        page_icon="⚙️",
        layout="wide",
    )

    st.title("KOMBAJN AI · Control Panel")
    
    tab1, tab2 = st.tabs(["📺 Video Orchestration", "🗓️ Datetime Scenario"])

    with tab1:
        st.subheader("Video Generator (JSON Manifest)")
        st.caption("Unified Pydantic v2 validation (Single Source of Truth).")
        
        # Example manifest for startup
        example = VideoEditManifest(
            project_id="atomic_tracer_bullet",
            width=1080,
            height=1920,
            fps=24,
            scenes=[
                {
                    "background": {"type": "color", "color": "black", "duration": 3.0},
                    "elements": [
                        {"type": "text", "text": "SCENE ONE", "fontsize": 120, "color": "#6897bb", "position": "center", "start_time": 0.0},
                        {"type": "text", "text": "Black Background", "fontsize": 60, "color": "white", "position": ["center", 1100], "start_time": 1.0}
                    ]
                },
                {
                    "background": {"type": "color", "color": "#3c3f41", "duration": 4.0},
                    "elements": [
                        {"type": "text", "text": "SCENE TWO", "fontsize": 120, "color": "#6a8759", "position": "center", "start_time": 0.0},
                        {"type": "text", "text": "Gray Background", "fontsize": 60, "color": "white", "position": ["center", 1100], "start_time": 1.0}
                    ]
                }
            ]
        )

        manifest_input = st.text_area(
            "Enter Manifest (JSON)", 
            value=json.dumps(example.model_dump(), indent=2),
            height=400
        )

        if st.button("Submit Render Task"):
            try:
                # 1. Pydantic v2 Validation (checks types, fields, etc. against schemas.py)
                manifest_obj = VideoEditManifest(**json.loads(manifest_input))
                
                # 2. Push to API
                data = _post_api("/tasks/generate-video", manifest_obj)
                st.success(f"Task submitted! Task ID: {data.get('task_id')}")
                st.session_state["last_task_id"] = data.get("task_id")
            except ValidationError as e:
                st.error(f"Model Validation Error: {e.json()}")
            except Exception as exc:
                st.error(f"Error: {exc}")

    with tab2:
        st.subheader("Datetime → timestamp")
        
        with st.form("date_form"):
            iso_input = st.text_input("Datetime (ISO 8601)", value="2026-03-05T12:00:00Z")
            submitted = st.form_submit_button("Submit")
            
        if submitted:
            try:
                payload = DatetimeToTimestampRequest(datetime_iso=iso_input)
                data = _post_api("/tasks/datetime-to-timestamp", payload)
                st.success("Task submitted.")
                st.session_state["last_task_id"] = data.get("task_id")
            except ValidationError as e:
                st.error(f"Validation Error: {e}")
            except Exception as exc:
                st.error(f"Error during submission: {exc}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Last Task Status")

    last_id = st.session_state.get("last_task_id", "")
    task_id_input = st.sidebar.text_input("Task ID", value=last_id)

    if st.sidebar.button("Refresh Status") and task_id_input:
        try:
            status = _get_task(task_id_input)
            st.sidebar.json(status)
        except Exception as exc:
            st.sidebar.error(f"Error: {exc}")


if __name__ == "__main__":
    main()
