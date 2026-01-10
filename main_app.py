import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber
import io

# --- 1. FOUNDATION & SNASSY STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 20px;
        border: 2px solid #C5A059;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #C5A059; color: #002147; border: 2px solid #002147; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "english_level" not in st.session_state:
    st.session_state.english_level = "Pending"
if "progress" not in st.session_state:
    st.session_state.progress = {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0}
if "vault" not in st.session_state:
    st.session_state.vault = {}

# --- 3. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.get("mute", False): return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("temp.mp3"))
        with open("temp.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 4. THE GRAND ENTRANCE (LOGO & LOGIN) ---
if not st.session_state.authenticated:
    col_logo, _ = st.columns([1, 2])
    with col_logo:
        try:
            st.image("logo.png", width=350)
        except:
            st.markdown("""
                <div style="background-color: #002147; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; text-align: center;">
                    <h1 style="color: #C5A059; margin: 0; font-family: 'Times New Roman';">🏛️</h1>
                    <h2 style="color: #C5A059; margin: 0; letter-spacing: 2px;">SIR RYAN'S ACADEMY</h2>
                    <p style="color: #C5A059; font-style: italic;">English Excellence & Honour</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:", key="reg_name")
        nick_in = st.text_input("Nickname:", key="reg_nick")
        u_photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        key_in = st.text_input("License Key:", type="password", key="reg_key")
        if st.button("Register & Begin Placement Exam"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.session_state.avatar = u_photo
                st.rerun()
            else:
                st.warning("Please ensure the name is filled and the key is correct.")
    st.stop()

# --- 5. LEVEL ASSESSMENT ---
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    st.title("📜 Entrance Evaluation")
    st.markdown(f"### Welcome, {st.session_state.nickname}. Please complete your 10-question placement exam.")
    
    with st.form("level_test_form"):
        q1 = st.radio("
