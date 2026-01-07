import streamlit as st
from groq import Groq
import pypdf
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import requests
import urllib.parse
import pandas as pd
from io import BytesIO

# --- 1. PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# --- 2. THEME (Oxford Blue & Gold with High Visibility) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F4F7F6; }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] { 
        background-color: #002147 !important; 
    }
    
    /* FORCE WHITE TEXT IN SIDEBAR */
    /* This targets headers, normal text, and labels */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stText {
        color: #FFFFFF !important;
    }

    /* Professional Buttons (Gold) */
    .stButton>button { 
        background-color: #C5A059 !important; 
        color: #002147 !important; /* Navy text on Gold button is easier to read */
        font-weight: bold !important;
        border-radius: 4px !important; 
    }
    
    /* File Uploader Text Fix */
    [data-testid="stSidebar"] .stFileUploader section {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "merits" not in st.session_state:
    st.session_state.merits = 0
if "gradebook" not in st.session_state:
    st.session_state.gradebook = []
if "student_name" not in st.session_state:
    st.session_state.student_name = "Scholar"

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Academy")
    st.write("Please enter your credentials for the 2026/2027 Recruitment Season.")
    
    name_input = st.text_input("Name for the Register:", placeholder="e.g. Master John")
    license_key = st.text_input("License Key:", type="password")
    
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.success("Access Granted. Opening the Academy...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("I'm afraid that key doesn't fit the lock, old sport.")
    st.stop()

# --- 5. HELPER FUNCTIONS ---
def speak_text(text):
    clean_text = text.replace("**", "").replace(":", ".").replace("_", "").replace("#", "")
    filename = "academy_voice.mp3"
    try:
        communicate = edge_tts.Communicate(clean_text, "en-GB-RyanNeural")
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("📖 Academy Handbook")
    with st.expander("How to Use", expanded=True):
        st.write("1. Upload Workbook\n2. Talk to Sir Ryan\n3. Practice STAR Method")
    
    uploaded_file = st.file_uploader("Upload Course PDF", type="pdf")
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([page.extract_text() for page in reader.pages])
        st.success("Workbook Filed!")

    if st.button("🧹 Reset Session"):
        st.session_state.clear()
        st.rerun()
    
    st.caption("© 2026 | Sir Ryan's Academy")

# --- 7. MAIN INTERFACE ---
st.title(f"🎓 Sir Ryan's Academy")
st.subheader(f"Welcome, {st.session_state.student_name}")

# Chat Hub
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        context = st.session_state.get("pdf_text", "")[:8000]
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Context: {context}. Use British-isms and spelling."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        speak_text(response)
