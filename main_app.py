import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber
import io

# --- 1. FOUNDATION & STYLING ---
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
    }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "english_level" not in st.session_state:
    st.session_state.english_level = "Pending"
if "vault" not in st.session_state:
    st.session_state.vault = {}
if "avatar" not in st.session_state:
    st.session_state.avatar = None

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

# --- 4. SHARED LOGO FUNCTION ---
def display_academy_logo(width=350):
    try:
        st.image("logo.png", width=width)
    except:
        st.markdown(f"""
            <div style="background-color: #002147; padding: 10px; border-radius: 10px; border: 2px solid #C5A059; text-align: center; width: {width}px;">
                <h2 style="color: #C5A059; margin: 0; font-family: 'Times New Roman';">🏛️ SIR RYAN'S ACADEMY</h2>
            </div>
        """, unsafe_allow_html=True)

# --- 5. THE LOGIN GATE ---
if not st.session_state.authenticated:
    display_academy_logo()
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:", key="reg_name")
        nick_in = st.text_input("Nickname:", key="reg_nick")
        u_photo = st.file_uploader("Upload Portrait for Academy Records:", type=['png', 'jpg', 'jpeg'], key="reg_photo")
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
                st.warning("Ensure the name is filled and the key is 'oxford2026'.")
    st.stop()

# --- 6. ENTRANCE EVALUATION ---
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    display_academy_logo(width=200)
    st.title("📜 Entrance Evaluation")
    with st.form("level_test"):
        st.radio("1. Which spelling is the British colour?", ["Color", "Colour"], key="e1")
        st.radio("2. A 'biscuit' is usually served with...", ["Tea", "Coffee"], key="e2")
        st.radio("3. Correct this: 'I has been here.'", ["I have been here.", "I was being here."], key="e3")
        if st.form_submit_button("Submit Assessment"):
            st.session_state.english_level = "Scholar"
            st.rerun()
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    display_academy_logo(width=200)
    st.divider()
    if st.session_state.get("avatar"):
        st.image(st.session_state.avatar, caption="Academy Portrait", use_container_width=True)
    st.markdown(f"### 👤 {st.session_state.get('nickname')}")
    st.info(f"🏅 Rank: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox
