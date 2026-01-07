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

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓", layout="wide")

# --- 2. THEME (Oxford Blue & Gold with High Visibility) ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #002147 !important; min-width: 300px; }
    
    /* High Visibility Sidebar Text */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }

    /* Professional Buttons */
    .stButton>button { 
        background-color: #C5A059 !important; 
        color: #002147 !important; 
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATES ---
initial_states = {
    "authenticated": False, "messages": [], "merits": 0, "gradebook": [], 
    "student_name": "Scholar", "pdf_text": "", "streak_count": 1, 
    "last_visit": datetime.date.today(), "english_level": None,
    "current_subject": "General Knowledge"
}
for key, val in initial_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Executive Academy")
    st.info("Enter your credentials for the 2026/2027 Season.")
    name_input = st.text_input("Name for the Register:")
    license_key = st.text_input("License Key:", type="password")
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.rerun()
        else: st.error("Access Denied, old sport.")
    st.stop()

# --- 5. SIR RYAN'S VOICE ---
def speak_text(text):
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("v.mp3"))
        with open("v.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- 6. PLACEMENT TEST (ONLY RUN ONCE) ---
if st.session_state.english_level is None:
    st.title(f"🎓 Welcome, {st.session_state.student_name}!")
    with st.container(border=True):
        st.subheader("Placement Evaluation")
        path = st.radio("Proceed:", ["I know my level", "Test me!"], horizontal=True)
        if path == "I know my level":
            lvl = st.selectbox("Rank:", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Confirm"):
                st.session_state.english_level = lvl
                st.rerun()
        else:
            ans = st.text_input("If I ___ (be) you, I'd study. (Fill blank):")
            if st.button("Submit"):
                st.session_state.english_level = "Advanced" if "were" in ans.lower() else "Beginner"
                st.rerun()
    st.stop()

# --- 7. SIDEBAR (THE FULL KIT) ---
with st.sidebar:
    st.header("📖 Academy Handbook")
    with st.expander("Usage Protocol"):
        st.write("1. Upload Course PDF\n2. Select Subject\n3. Engage Sir Ryan")
    
    st.header("📜 Academy Library")
    uploaded_file = st.file_uploader("Upload Workbook", type="pdf")
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
        st.success("Archives Updated!")

    st.header("📚 Subject Registry")
    st.session_state.current_subject = st.selectbox("Field of Study:", ["English", "Medicine", "Business", "General Knowledge"])

    st.header("📜 Gradebook")
    if st.session_state.gradebook: st.table(pd.DataFrame(st.session_state.gradebook))
    
    with st.expander("🇬🇧 British Idioms"):
        st.write("* 'Chuffed to bits': Happy\n* 'A spot of bother': A problem")

    try:
        weather = requests.get("https://wttr.in/London?format=%c+%t").text
        st.info(f"🇬🇧 London: {weather}")
    except: pass

    st.link_button("💬 WhatsApp Dean", f"https://wa.me/27833976517")
    if st.button("🧹 Reset"):
        st.session_state.clear()
        st.rerun()

# --- 8. THE STUDY HALL ---
st.markdown(f"<h1 style='text-align: center; color: #002147;'>🎓 Sir Ryan’s Academy</h1>", unsafe_allow_html=True)
st.write(f"### Welcome, {st.session_state.student_name} | {st.session_state.english_level} Level")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Save")
    if rec: 
        st.audio(rec['bytes'])
        if st.button("Submit Recording"):
            st.session_state.gradebook.append({"Subject": "Oral", "Grade": "A+"})
            st.balloons()

with col2:
    st.subheader("🔥 Study Progress")
    st.metric("Streak", f"{st.session_state.streak_count} Days")
    st.metric("Merits", st.session_state.merits)

# Chat Hub
st.divider()
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Speak with the Headmaster..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        ctx = st.session_state.pdf_text[:8000]
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Context: {ctx}. Focus on the STAR method. Use British spelling and biscuits!"}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)
