import os
import json
from typing import Any, Dict, List
from pathlib import Path

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.engine.j2v_types import J2VMovie, J2VScene, ImageElement, TextElement, ELEMENT_MODEL_MAP
from backend.app.engine.ui_builder import pydantic_form
from backend.app.engine.project_store import ProjectStore
from backend.app.engine.asset_manager import AssetManager


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")
STORE_PATH = os.getenv("PROJECT_STORE_PATH", "/data/projects")
ASSET_PATH = os.getenv("ASSET_PATH", "/data/assets")
MANIFESTS_PATH = Path("backend/app/tests/manifests")

store = ProjectStore(STORE_PATH)
asset_mgr = AssetManager(ASSET_PATH)


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


def main() -> None:
    st.set_page_config(page_title="KOMBAJN AI Studio", page_icon="🎬", layout="wide")
    st.title("🎬 J2V Professional Video Studio")
    
    tab1, tab2 = st.tabs(["🏗️ J2V Composer", "🔍 Monitoring"])

    if "current_manifest" not in st.session_state:
        st.session_state["current_manifest"] = get_empty_manifest()

    with tab1:
        # --- PROJECT ACTIONS ---
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            projects = store.list_projects()
            options = ["-- New Empty Project --"] + projects
            sel = c1.selectbox("📁 Saved Projects", options)
            
            if sel != "-- New Empty Project --" and st.session_state.get("last_loaded") != sel:
                st.session_state["current_manifest"] = store.load_project(sel)
                st.session_state["last_loaded"] = sel; st.rerun()
            elif sel == "-- New Empty Project --" and st.session_state.get("last_loaded") is not None:
                st.session_state["current_manifest"] = get_empty_manifest()
                st.session_state["last_loaded"] = None; st.rerun()
            
            proj_name = c2.text_input("Project Name", value=st.session_state.get("last_loaded") or "my_video")
            if c3.button("💾 SAVE", use_container_width=True):
                store.save_project(proj_name, st.session_state["current_manifest"])
                st.toast(f"Saved to {proj_name}.json")
            if c4.button("🗑️ CLEAR", use_container_width=True):
                st.session_state["current_manifest"] = get_empty_manifest()
                st.session_state["last_loaded"] = None; st.rerun()

        # --- MANIFEST LIBRARY ---
        with st.expander("📂 Manifest Library (Pre-baked Demos)", expanded=True):
            manifest_files = [f.name for f in MANIFESTS_PATH.glob("*.json")]
            cols = st.columns(max(len(manifest_files), 4))
            for idx, m_file in enumerate(manifest_files):
                if cols[idx].button(f"Load {m_file}", use_container_width=True):
                    with open(MANIFESTS_PATH / m_file, "r") as f:
                        st.session_state["current_manifest"] = json.load(f)
                    st.toast(f"Loaded {m_file}")
                    st.rerun()

        # --- MAIN LAYOUT ---
        col_ed, col_pre = st.columns([3, 2])
        m = st.session_state["current_manifest"]

        with col_ed:
            with st.expander("🌍 GLOBAL MOVIE SETTINGS", expanded=False):
                movie_data = pydantic_form(J2VMovie, key_prefix="movie_glob", initial_data=m, exclude_fields=["scenes", "elements"], asset_mgr=asset_mgr)
                for k, v in movie_data.items(): m[k] = v

            st.markdown("---")
            st.subheader("🎬 Scenes")
            
            new_scenes = []
            for i, scene_data in enumerate(m.get("scenes", [])):
                with st.container(border=True):
                    sc_head1, sc_head2 = st.columns([4, 1])
                    sc_head1.write(f"### Scene #{i+1}")
                    if sc_head2.button("❌ Remove", key=f"del_sc_{i}"):
                        m["scenes"].pop(i); st.rerun()
                    
                    updated_scene = pydantic_form(J2VScene, key_prefix=f"sc_{i}", initial_data=scene_data, exclude_fields=["elements"], asset_mgr=asset_mgr)
                    
                    st.write("**Elements**")
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
                            
                            updated_el = pydantic_form(el_model, key_prefix=f"el_{i}_{j}", initial_data=el_data, asset_mgr=asset_mgr)
                            new_elements.append(updated_el)
                    
                    add_c1, add_c2 = st.columns([3, 1])
                    el_type_to_add = add_c1.selectbox("Add element", list(ELEMENT_MODEL_MAP.keys()), key=f"add_el_sel_{i}")
                    if add_c2.button("➕ ADD", key=f"add_el_btn_{i}", use_container_width=True):
                        if "elements" not in scene_data: scene_data["elements"] = []
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
                valid_obj = J2VMovie(**m)
                final_json = valid_obj.model_dump(by_alias=True)
                st.success("✅ Manifest is valid")
                if st.button("🔥 START RENDERING", use_container_width=True, type="primary"):
                    res = _post_api("/tasks/j2v-render", valid_obj)
                    st.balloons(); st.session_state["last_task_id"] = res.get("task_id"); st.success(f"Task ID: {res.get('task_id')}")
            except ValidationError as e:
                st.error(f"❌ Errors: {e.error_count()}")
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
