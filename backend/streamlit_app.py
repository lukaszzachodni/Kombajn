import os
import json
from typing import Any, Dict

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.schemas import DatetimeToTimestampRequest, VideoEditManifest
from backend.app.engine.j2v_types import J2VMovie, J2VScene
from backend.app.engine.j2v_models import ELEMENT_MODEL_MAP
from backend.app.engine.ui_builder import pydantic_form
from backend.app.engine.project_store import ProjectStore


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")
STORE_PATH = os.getenv("PROJECT_STORE_PATH", "/data/projects")
store = ProjectStore(STORE_PATH)


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
    
    tab1, tab2, tab3 = st.tabs(["📺 Video Orchestration", "🎬 J2V Local Clone", "🗓️ Datetime Scenario"])

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
        st.subheader("J2V Local Clone - Project Manager")
        
        # 1. Project Management
        col_list, col_new = st.columns([3, 1])
        
        with col_list:
            projects = store.list_projects()
            selected_proj = st.selectbox("📁 Load Existing Project", ["-- New Project --"] + projects)
        
        with col_new:
            new_proj_name = st.text_input("📝 Save as New Name", placeholder="my_cool_video")

        # Handle loading logic
        if "current_manifest" not in st.session_state:
            st.session_state["current_manifest"] = {}
            st.session_state["last_loaded"] = None

        if selected_proj != "-- New Project --" and st.session_state.get("last_loaded") != selected_proj:
            st.session_state["current_manifest"] = store.load_project(selected_proj)
            st.session_state["last_loaded"] = selected_proj
            st.rerun()
        elif selected_proj == "-- New Project --" and st.session_state.get("last_loaded") is not None:
            st.session_state["current_manifest"] = {}
            st.session_state["last_loaded"] = None
            st.rerun()

        st.markdown("---")
        st.subheader("Configuration")
        
        with st.expander("Movie Settings", expanded=True):
            movie_data = pydantic_form(
                J2VMovie, 
                key_prefix="j2v_movie", 
                registry=ELEMENT_MODEL_MAP,
                initial_data=st.session_state["current_manifest"]
            )
            
        st.write("### Generated Manifest Preview")
        st.code(json.dumps(movie_data, indent=2))
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            save_name = new_proj_name if new_proj_name else (selected_proj if selected_proj != "-- New Project --" else None)
            if st.button("💾 Save Project") and save_name:
                store.save_project(save_name, movie_data)
                st.success(f"Project '{save_name}' saved!")
                st.session_state["last_loaded"] = save_name
                st.rerun()
        
        with col_s2:
            if st.button("📥 Download Manifest"):
                st.download_button(
                    label="Confirm Download",
                    data=json.dumps(movie_data, indent=2),
                    file_name="j2v_manifest.json",
                    mime="application/json"
                )
        with col_s3:
            if st.button("🚀 Submit to Local J2V Renderer"):
                try:
                    # Validate first
                    manifest_obj = J2VMovie(**movie_data)
                    # Submit to API
                    data = _post_api("/tasks/j2v-render", manifest_obj)
                    st.success(f"J2V Render Task submitted! Task ID: {data.get('task_id')}")
                    st.session_state["last_task_id"] = data.get("task_id")
                except ValidationError as e:
                    st.error(f"Validation Error: {e.json()}")
                except Exception as exc:
                    st.error(f"Error: {exc}")

    with tab3:
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
