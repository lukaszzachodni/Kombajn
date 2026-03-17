import os
import json
from typing import Any, Dict, List

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.schemas import DatetimeToTimestampRequest, VideoEditManifest
from backend.app.engine.j2v_types import J2VMovie, J2VScene, ImageElement, TextElement
from backend.app.engine.j2v_models import ELEMENT_MODEL_MAP
from backend.app.engine.ui_builder import pydantic_form
from backend.app.engine.project_store import ProjectStore


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")
STORE_PATH = os.getenv("PROJECT_STORE_PATH", "/data/projects")
store = ProjectStore(STORE_PATH)


def _post_api(endpoint: str, payload: Any) -> Dict[str, Any]:
    json_data = payload.model_dump(by_alias=True) if hasattr(payload, "model_dump") else payload
    resp = requests.post(f"{API_BASE}{endpoint}", json=json_data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_task(task_id: str) -> Dict[str, Any]:
    resp = requests.get(f"{API_BASE}/tasks/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_empty_manifest():
    return {"width": 1080, "height": 1920, "fps": 24, "scenes": [], "variables": {}}

def get_demo_manifest():
    return {
        "width": 1080, "height": 1920, "fps": 24,
        "variables": {"main_title": "MY MOVIE"},
        "scenes": [
            {
                "background-color": "#FF5733", "duration": 5.0,
                "elements": [{"type": "text", "text": "SCENE 1", "settings": {"font-size": 100, "font-color": "white"}}]
            },
            {
                "background-color": "#33FF57", "duration": 5.0,
                "elements": [{"type": "text", "text": "SCENE 2", "settings": {"font-size": 100, "font-color": "white"}}]
            }
        ]
    }


def main() -> None:
    st.set_page_config(page_title="KOMBAJN AI Studio", page_icon="🎬", layout="wide")
    st.title("🎬 KOMBAJN AI · Professional Video Studio")
    
    tab1, tab2 = st.tabs(["🏗️ J2V Composer", "🔍 Monitoring"])

    if "current_manifest" not in st.session_state:
        st.session_state["current_manifest"] = get_empty_manifest()

    with tab1:
        # --- TOP BAR: Project Actions ---
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            projects = store.list_projects()
            options = ["-- New Empty Project --", "🚀 LOAD DEMO"] + projects
            sel = c1.selectbox("📁 Projects", options)
            
            if sel == "🚀 LOAD DEMO" and st.session_state.get("last_loaded") != "demo":
                st.session_state["current_manifest"] = get_demo_manifest()
                st.session_state["last_loaded"] = "demo"; st.rerun()
            elif sel == "-- New Empty Project --" and st.session_state.get("last_loaded") is not None:
                st.session_state["current_manifest"] = get_empty_manifest()
                st.session_state["last_loaded"] = None; st.rerun()
            elif sel not in ["-- New Empty Project --", "🚀 LOAD DEMO"] and st.session_state.get("last_loaded") != sel:
                st.session_state["current_manifest"] = store.load_project(sel)
                st.session_state["last_loaded"] = sel; st.rerun()
            
            proj_name = c2.text_input("Project Name", value=st.session_state.get("last_loaded") or "my_video")
            if c3.button("💾 SAVE", use_container_width=True):
                store.save_project(proj_name, st.session_state["current_manifest"])
                st.toast(f"Saved to {proj_name}.json")
            if c4.button("🗑️ CLEAR", use_container_width=True):
                st.session_state["current_manifest"] = get_empty_manifest()
                st.rerun()

        # --- MAIN LAYOUT ---
        col_ed, col_pre = st.columns([3, 2])
        m = st.session_state["current_manifest"]

        with col_ed:
            # 1. MOVIE GLOBAL SETTINGS
            with st.expander("🌍 GLOBAL MOVIE SETTINGS", expanded=False):
                movie_data = pydantic_form(J2VMovie, key_prefix="movie_glob", initial_data=m, exclude_fields=["scenes", "elements"])
                # Update root manifest with basic fields
                for k, v in movie_data.items(): m[k] = v

            st.markdown("---")
            
            # 2. SCENES
            st.subheader("🎬 Scenes")
            if not m.get("scenes"): st.info("Add a scene to start.")
            
            new_scenes = []
            for i, scene_data in enumerate(m.get("scenes", [])):
                with st.container(border=True):
                    sc_head1, sc_head2 = st.columns([4, 1])
                    sc_head1.write(f"### Scene #{i+1}")
                    if sc_head2.button("❌ Remove", key=f"del_sc_{i}"):
                        m["scenes"].pop(i); st.rerun()
                    
                    # Scene Base Properties (using pydantic_form for ALL fields)
                    updated_scene = pydantic_form(J2VScene, key_prefix=f"sc_{i}", initial_data=scene_data, exclude_fields=["elements"])
                    
                    # 3. ELEMENTS IN SCENE
                    st.write("---")
                    st.write("**Elements in this scene**")
                    elements = scene_data.get("elements", [])
                    new_elements = []
                    
                    for j, el_data in enumerate(elements):
                        el_type = el_data.get("type", "text")
                        el_model = ELEMENT_MODEL_MAP.get(el_type, TextElement)
                        
                        with st.container(border=True):
                            el_c1, el_c2 = st.columns([4, 1])
                            el_c1.caption(f"ELEMENT: {el_type.upper()}")
                            if el_c2.button("🗑️", key=f"del_el_{i}_{j}"):
                                elements.pop(j); st.rerun()
                            
                            # Render ALL fields for this specific element type
                            updated_el = pydantic_form(el_model, key_prefix=f"el_{i}_{j}", initial_data=el_data)
                            new_elements.append(updated_el)
                    
                    # Add Element Logic
                    add_c1, add_c2 = st.columns([3, 1])
                    el_type_to_add = add_c1.selectbox("Add element", list(ELEMENT_MODEL_MAP.keys()), key=f"add_el_sel_{i}")
                    if add_c2.button("➕ ADD", key=f"add_el_btn_{i}", use_container_width=True):
                        if "elements" not in scene_data: scene_data["elements"] = []
                        # Initialize with correct default type
                        scene_data["elements"].append({"type": el_type_to_add})
                        st.rerun()
                    
                    updated_scene["elements"] = new_elements
                    new_scenes.append(updated_scene)
            
            m["scenes"] = new_scenes
            
            if st.button("🚀 ADD NEW SCENE", use_container_width=True):
                m["scenes"].append({"background-color": "#000000", "duration": 5.0, "elements": []})
                st.rerun()

        with col_pre:
            st.subheader("👁️ Preview & Render")
            try:
                # Full Validation
                valid_obj = J2VMovie(**m)
                final_json = valid_obj.model_dump(by_alias=True)
                st.success("✅ Manifest is 100% valid and documented.")
                
                if st.button("🔥 START RENDERING", use_container_width=True, type="primary"):
                    res = _post_api("/tasks/j2v-render", valid_obj)
                    st.balloons()
                    st.session_state["last_task_id"] = res.get("task_id")
                    st.success(f"Task submitted! ID: {res.get('task_id')}")
            except ValidationError as e:
                st.error(f"❌ Validation Errors: {e.error_count()}")
                for err in e.errors()[:3]: 
                    st.caption(f"**{'.'.join(str(x) for x in err['loc'])}**: {err['msg']}")
                final_json = m
            
            st.code(json.dumps(final_json, indent=2), language="json")

    with tab2:
        st.subheader("Task Status")
        last_id = st.session_state.get("last_task_id", "")
        tid = st.text_input("Task ID", value=last_id)
        if st.button("Refresh"):
            try: st.json(_get_task(tid))
            except Exception as e: st.error(str(e))

if __name__ == "__main__":
    main()
