import streamlit as st
import requests
import os
import json
from PIL import Image

st.set_page_config(page_title="ColorBook Studio", page_icon="📚", layout="wide")

api_base = os.getenv("KOMBAJN_API_BASE", "http://api:8000")

st.title("📚 ColorBook Studio")

tabs = st.tabs(["New Project", "Project Browser"])

# --- TAB: NEW PROJECT ---
with tabs[0]:
    st.sidebar.header("Configuration")
    idea = st.text_input("Book Idea", placeholder="e.g. Dragons in space")
    page_limit = st.slider("Page Limit", 1, 100, 40)

    if st.button("Initialize Project"):
        if idea:
            try:
                response = requests.post(f"{api_base}/color-book/init", json={"idea": idea, "page_limit": page_limit})
                if response.status_code == 200:
                    st.success(f"Project initialized! Task ID: {response.json().get('task_id')}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
        else:
            st.warning("Please provide an idea.")

# --- TAB: PROJECT BROWSER ---
with tabs[1]:
    try:
        resp = requests.get(f"{api_base}/color-book/projects")
        if resp.status_code == 200:
            projects = resp.json().get("projects", [])
            selected_project = st.selectbox("Select Project", projects)
            
            if selected_project:
                p_resp = requests.get(f"{api_base}/color-book/projects/{selected_project}")
                if p_resp.status_code == 200:
                    p_data = p_resp.json()
                    data = p_data["data"]
                    files = p_data["files"]
                    
                    st.header(f"Project: {selected_project}")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Project Data")
                        details = data.get("coloringBook", {}).get("mainProjectDetails", {})
                        st.json(details)
                        
                        st.subheader("Page Prompts")
                        prompts = data.get("coloringBook", {}).get("pagePromptLibrary", [])
                        for p in prompts:
                            with st.expander(f"Page {p['promptId']}"):
                                st.write(p["sceneDescription"])
                                if st.button(f"Regenerate Page {p['promptId']}", key=f"reg_{p['promptId']}"):
                                    # Tu logika wysłania regenu
                                    st.info("Regeneration started...")

                    with col2:
                        st.subheader("Files")
                        for f in files:
                            if f["type"] in ["png", "jpg"]:
                                # Streamlit nie może czytać bezpośrednio z /data/projects/{id}
                                # jeśli nie jest on zmapowany jako static.
                                # Ale w kontenerze app mamy /app/data/projects
                                st.image(f["path"], caption=f["name"])
                            else:
                                st.write(f"📄 {f['name']} ({f['type']})")
                else:
                    st.error("Failed to load project details.")
        else:
            st.error("Failed to fetch projects list.")
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.subheader("System Status")
st.info("Use Flower to track Celery tasks.")
