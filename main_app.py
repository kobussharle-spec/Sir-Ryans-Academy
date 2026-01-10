import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# Snassy Styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 20px;
        border: 2px solid #C5A059;
        font-weight: bold;
    }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #002147; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "current_subject": "General English",
        "progress": {"Grammar": 45, "Tenses": 30, "Vocab": 60, "Business": 20},
        "vault": {}
    })

# --- 3. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.mute: return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("temp.mp3"))
        with open("temp.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        # FIXED LINE BELOW:
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: 
        pass
