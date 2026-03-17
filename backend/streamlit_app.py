import os
import json
from typing import Any, Dict, List

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.schemas import DatetimeToTimestampRequest, VideoEditManifest
from backend.app.engine.j2v_types import J2VMovie, J2VScene, ImageElement, TextElement
from backend.app.engine.j2v_models import ELEMENT_MODEL_MAP
from backend.app.engine.project_store import ProjectStore


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")
STORE_PATH = os.getenv("PROJECT_STORE_PATH", "/data/projects")
store = ProjectStore(STORE_PATH)


def _post_api(endpoint: str, payload: Any) -> Dict[str, Any]:
    """Common helper to push data to the API."""
    json_data = payload.model_dump(by_alias=True) if hasattr(payload, "model_dump") else payload
    resp = requests.post(f"{API_BASE}{endpoint}", json=json_data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_task(task_id: str) -> Dict[str, Any]:
    resp = requests.get(f"{API_BASE}/tasks/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_default_manifest():
    """Returns the requested 10s two-scene starter."""
    return {
        "width": 1080,
        "height": 1920,
        "fps": 24,
        "scenes": [
            {
                "background-color": "#FF5733",
                "duration": 5.0,
                "comment": "Scene 1 starter",
                "elements": [
                    {"type": "text", "text": "SCENE 1", "style": "001", "settings": {"font-size": 100, "font-color": "white", "vertical-position": "center"}}
                ]
            },
            {
                "background-color": "#33FF57",
                "duration": 5.0,
                "comment": "Scene 2 starter",
                "elements": [
                    {"type": "text", "text": "SCENE 2", "style": "001", "settings": {"font-size": 100, "font-color": "white", "vertical-position": "center"}}
                ]
            }
        ]
    }


def main() -> None:
    st.set_page_config(page_title="KOMBAJN AI", page_icon="⚙️", layout="wide")
    st.title("KOMBAJN AI · Video Studio")
    
    tab1, tab2 = st.tabs(["🎬 J2V Local Clone (Composer)", "🗓️ Tasks & Others"])

    if "current_manifest" not in st.session_state:
        st.session_state["current_manifest"] = get_default_manifest()

    with tab1:
        # --- Project Header ---
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            projects = store.list_projects()
            sel = c1.selectbox("📁 Load Project", ["-- New Project --"] + projects)
            if sel != "-- New Project --" and st.session_state.get("last_loaded") != sel:
                st.session_state["current_manifest"] = store.load_project(sel)
                st.session_state["last_loaded"] = sel
                st.rerun()
            elif sel == "-- New Project --" and st.session_state.get("last_loaded") is not None:
                st.session_state["current_manifest"] = get_default_manifest()
                st.session_state["last_loaded"] = None
                st.rerun()
            
            proj_name = c2.text_input("📝 Save Name", value=st.session_state.get("last_loaded") or "my_video")
            if c3.button("💾 Save"):
                store.save_project(proj_name, st.session_state["current_manifest"])
                st.toast(f"Saved {proj_name}")
            if c4.button("🧹 Reset"):
                st.session_state["current_manifest"] = get_default_manifest()
                st.rerun()

        # --- Layout: Editor | Preview ---
        col_ed, col_pre = st.columns([3, 2])

        with col_ed:
            st.subheader("🛠️ Video Settings")
            m = st.session_state["current_manifest"]
            cc1, cc2, cc3 = st.columns(3)
            m["width"] = cc1.number_input("Width", value=m.get("width", 1080))
            m["height"] = cc2.number_input("Height", value=m.get("height", 1920))
            m["fps"] = cc3.number_input("FPS", value=m.get("fps", 24))

            st.markdown("---")
            st.subheader("🎬 Scenes")
            
            for i, scene in enumerate(m.get("scenes", [])):
                with st.expander(f"Scene #{i+1} ({scene.get('duration')}s)", expanded=True):
                    sc1, sc2, sc3 = st.columns([2, 1, 1])
                    scene["background-color"] = sc1.color_picker("BG Color", value=scene.get("background-color", "#000000"), key=f"bg_{i}")
                    scene["duration"] = sc2.number_input("Duration (s)", value=float(scene.get("duration", 5.0)), key=f"dur_{i}")
                    if sc3.button("🗑️ Delete Scene", key=f"del_sc_{i}"):
                        m["scenes"].pop(i)
                        st.rerun()
                    
                    st.write("**Elements**")
                    for j, el in enumerate(scene.get("elements", [])):
                        with st.container(border=True):
                            ec1, ec2, ec3 = st.columns([1, 3, 1])
                            ec1.caption(f"{el.get('type').upper()}")
                            
                            if el["type"] == "text":
                                el["text"] = ec2.text_input("Text", value=el.get("text", ""), key=f"txt_{i}_{j}")
                            elif el["type"] == "image":
                                el["src"] = ec2.text_input("Image URL / Path", value=el.get("src", ""), key=f"img_{i}_{j}")
                            
                            if ec3.button("🗑️", key=f"del_el_{i}_{j}"):
                                scene["elements"].pop(j)
                                st.rerun()
                    
                    # Add Element Buttons
                    btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("➕ Add Text", key=f"add_txt_{i}"):
                        scene["elements"].append({"type": "text", "text": "New Text", "style": "001", "settings": {"font-size": 80, "font-color": "white"}})
                        st.rerun()
                    if btn_c2.button("➕ Add Image", key=f"add_img_{i}"):
                        scene["elements"].append({"type": "image", "src": "/data/assets/images/placeholder.png", "position": "center-center"})
                        st.rerun()

            if st.button("🚀 Add New Scene"):
                m["scenes"].append({"background-color": "#000000", "duration": 5.0, "elements": []})
                st.rerun()

        with col_pre:
            st.subheader("👁️ JSON Preview & Render")
            try:
                # Validation
                valid_obj = J2VMovie(**m)
                final_json = valid_obj.model_dump(by_alias=True)
                st.success("✅ Manifest is valid")
                
                if st.button("🔥 RENDER VIDEO", use_container_width=True, type="primary"):
                    res = _post_api("/tasks/j2v-render", valid_obj)
                    st.balloons()
                    st.session_state["last_task_id"] = res.get("task_id")
                    st.success(f"Rendering started! Task ID: {res.get('task_id')}")
            except ValidationError as e:
                st.error(f"❌ Invalid Data: {e.error_count()} errors")
                final_json = m
            
            st.code(json.dumps(final_json, indent=2), language="json")

    with tab2:
        st.subheader("Task History")
        last_id = st.session_state.get("last_task_id", "")
        task_id_input = st.text_input("Enter Task ID to check", value=last_id)
        if st.button("Check Status"):
            try:
                status = _get_task(task_id_input)
                st.json(status)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
