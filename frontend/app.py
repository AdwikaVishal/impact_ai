import streamlit as st
import requests
import json

st.set_page_config(page_title="MarketShield AI Frontend", layout="wide")

st.title("🚀 MarketShield AI - Backend Frontend")
st.subheader("Production Backend Integration")

API_BASE = "http://localhost:8000/api/v1"

st.info("🧪 Backend structure created. Install deps: `pip install -r backend/requirements.txt`")
st.info("🚀 Test health: `curl http://localhost:8000/health` (after uvicorn)")

headline = st.text_area("Enter headline for future API integration")

if st.button("Test Backend Health"):
    try:
        resp = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
        st.success("Backend healthy!")
        st.json(resp.json())
    except:
        st.error("Backend not running. Run: `cd backend && uvicorn app.main:app --reload`")

# TODO: Integrate with /analyze/headline after API ready

