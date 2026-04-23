import streamlit as st
import requests
import os

st.set_page_config(page_title="ColorBook Studio", page_icon="📚", layout="wide")

st.title("📚 ColorBook Studio")
st.write("Welcome to the AI Coloring Book Generator.")

api_base = os.getenv("KOMBAJN_API_BASE", "http://api:8000")

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

st.divider()
st.subheader("Project Status")
st.info("Task monitoring coming soon. Use Flower to track progress.")
