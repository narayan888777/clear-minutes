import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="ClearMinutes AI", page_icon="🚀", layout="wide")

# Custom CSS to make it look like a premium product
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0052cc;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ClearMinutes AI")
st.subheader("Transform Meeting Transcripts into Jira Tasks")

# --- SIDEBAR: CLIENT SETTINGS ---
with st.sidebar:
    st.header("⚙️ Setup")
    st.info("Enter your Jira details below to connect the engine.")
    
    # These stay as inputs so your 12 clients can eventually use their own Jira
    jira_url = st.text_input("Jira URL", value="https://yashooda789.atlassian.net")
    email = st.text_input("Jira Email", value="yashooda789@gmail.com")
    api_token = st.text_input("Jira API Token", type="password", help="Get this from Atlassian Security settings.")
    project_key = st.text_input("Project Key", value="KAN")

# --- MAIN INTERFACE ---
col1, col2 = st.columns([2, 1])

with col1:
    transcript = st.text_area(
        "Paste your meeting transcript or notes here:", 
        placeholder="Example: Yash will fix the login bug. Sarah needs to design the logo by Tuesday.",
        height=300
    )

with col2:
    st.write("### Instructions")
    st.write("1. Paste your text on the left.")
    st.write("2. Ensure sentences use 'action words' (will, must, needs to, task).")
    st.write("3. Click the button below to sync.")

if st.button("Generate & Sync to Jira"):
    if not api_token:
        st.error("❌ Missing API Token! Please check the sidebar.")
    elif not transcript:
        st.warning("⚠️ Please paste a transcript first.")
    else:
        # Simple Logic Parser
        lines = transcript.split('.')
        # Filtering for lines that contain action keywords
        found_tasks = [l.strip() for l in lines if any(w in l.lower() for w in ['will', 'need', 'must', 'task', 'action'])]
        
        if not found_tasks:
            st.warning("🤔 No clear tasks identified. Try using more direct language like 'John will...'")
        else:
            st.success(f"🔍 Found {len(found_tasks)} action items!")
            
            for t in found_tasks:
                auth = HTTPBasicAuth(email, api_token)
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                
                payload = json.dumps({
                    "fields": {
                        "project": {"key": project_key},
                        "summary": t[:254], # Jira limit for summary
                        "description": f"Automatically extracted from meeting notes.\n\nOriginal text: {t}",
                        "issuetype": {"name": "Task"}
                    }
                })
                
                try:
                    res = requests.post(f"{jira_url}/rest/api/2/issue", headers=headers, data=payload, auth=auth)
                    if res.status_code == 201:
                        st.write(f"✅ **Created:** {t[:60]}...")
                    else:
                        st.error(f"❌ Failed to create task. Error: {res.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {e}")

st.divider()
st.caption("Powered by ClearMinutes AI Engine v1.0")
