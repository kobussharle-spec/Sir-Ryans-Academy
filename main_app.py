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

# --- THE PERMANENT ACADEMY ARCHIVE ---
# Paste your entire workbook text between the triple quotes below
WORKBOOK_TEXT = """
PASTE ALL YOUR PDF TEXT HERE...
(Day 1: The STAR Method...)
(Day 2: Professional Etiquette...)
(Day 3: Handling Difficult Questions...)
... AND SO ON.
"""

# --- THEN UPDATE YOUR INITIAL_STATES (Section 3) ---
initial_states = {
    "authenticated": False, 
    "messages": [], 
    "merits": 0, 
    "gradebook": [], 
    "student_name": "Scholar", 
    "pdf_text": WORKBOOK_TEXT, # <--- THIS IS THE KEY CHANGE
    "streak_count": 1, 
    "last_visit": datetime.date.today(), 
    "english_level": "Advanced",
    "current_subject": "Interview Prep (STAR Method)"
}

# --- 1. THE FOUNDATION (MUST BE FIRST) ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓", layout="wide")

# --- 2. THEME & VISIBILITY ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #002147 !important; min-width: 350px; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] li, [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
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
    "last_visit": datetime.date.today(), "english_level": "Advanced",
    "current_subject": "Interview Prep (STAR Method)"
}
for key, val in initial_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Executive Academy")
    name_input = st.text_input("Name for the Register:")
    license_key = st.text_input("License Key:", type="password")
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.rerun()
        else: st.error("Access Denied, old sport.")
    st.stop()

# --- 5. VOICE ENGINE (Forced Playback) ---
def speak_text(text):
    try:
        clean = text.replace("**", "").replace("#", "").replace("_", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        # Creating a unique filename to prevent browser caching
        ts = str(int(time.time()))
        filename = f"v_{ts}.mp3"
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(audio_html, unsafe_allow_html=True)
    except: pass

# --- 6. THE SIDEBAR (All Subjects & New Tools) ---
with st.sidebar:
    st.title("🏫 Academy Registry")
    
    # 6.1 SUBJECT SELECTION
    st.header("📚 Subject Registry")
    subject_list = [
        "English: Tenses", "English: Grammar", "English: Pronunciation",
        "English: Vocabulary", "English: Conversation", 
        "English: Writing - Emails", "English: Writing - Letters", "English: Writing - Reports",
        "Preparing for ELS", "Interview Prep (STAR Method)", "Business English", 
        "Medicine", "Law", "Engineering", "General Knowledge"
    ]
    st.session_state.current_subject = st.selectbox("Select Study Focus:", subject_list)

    # 6.2 ACADEMY LIBRARY (PDF Uploader)
    st.header("📜 Academy Library")
    uploaded_file = st.file_uploader("Upload Workbook (PDF)", type="pdf")
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
        st.success("Archives Updated!")

    # 6.3 THE USER MANUAL (NEW)
    with st.expander("📖 Academy User Manual", expanded=False):
        st.markdown("""
        **Welcome to the 2026 Edition!**
        * **Step 1:** Upload your course PDF in the 'Library' above.
        * **Step 2:** Select your subject (e.g., *Interview Prep*).
        * **Step 3:** Use the **Oral Exam** to record your STAR answers.
        * **Step 4:** Ask Sir Ryan to 'Quiz me' or 'Check my grammar'.
        * **The Golden Rule:** Always be polite, and remember to have a **biscuit** during breaks!
        """)

    # 6.4 THE FREE DICTIONARY (NEW)
    with st.expander("📕 Academy Dictionary", expanded=False):
        word = st.text_input("Look up a word:", placeholder="e.g. Quintessential").strip()
        if word:
            try:
                # Using a free, reliable Dictionary API
                res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
                if res.status_code == 200:
                    data = res.json()[0]
                    meaning = data['meanings'][0]['definitions'][0]['definition']
                    st.write(f"**Definition:** {meaning}")
                else:
                    st.warning("Word not found in the archives, old sport.")
            except:
                st.error("The Dictionary is currently being dusted.")

    # 6.5 EXTRAS
    with st.expander("🏛️ Resources & Idioms"):
        st.write("British Idioms: 'Chuffed', 'Spot of bother'")
        try:
            w = requests.get("https://wttr.in/London?format=%c+%t").text
            st.info(f"London: {w}")
        except: pass

    with st.expander("🔒 Privacy & Copyright"):
        st.write("© 2026 J Steenekamp | All Rights Reserved.")

    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🧹 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- 7. THE MAIN HUB (MUST BE OUTSIDE SIDEBAR BLOCK) ---
st.markdown(f"<h1 style='color: #002147;'>🎓 Sir Ryan’s Executive Academy</h1>", unsafe_allow_html=True)

# WELCOME LETTER
st.markdown(f"""
<div style="border: 3px solid #C5A059; padding: 20px; border-radius: 10px; background-color: white;">
    <h3 style="color: #002147;">📜 A Note from the Headmaster</h3>
    <p><b>To the Honourable {st.session_state.student_name},</b></p>
    <p>Welcome to your personal Study Hall. We shall master <b>{st.session_state.current_subject}</b> together.</p>
    <p>Please, have a <b>biscuit</b> and let us begin our work for the 2026/2027 season.</p>
    <p><i>Yours,</i> <b>Sir Ryan</b></p>
</div>
""", unsafe_allow_html=True)

# TOOLS
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Save")
    if rec: 
        st.audio(rec['bytes'])
        if st.button("Submit Recording"): st.success("Graded!")

with col_b:
    st.subheader("📝 Quick Actions")
    if st.button("📝 Start Quiz"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, please quiz me!"})
        st.rerun()

# CHAT
st.divider()
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Consulting..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            ctx = st.session_state.pdf_text[:8000]
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Context: {ctx}. Focus: {st.session_state.current_subject}. Use British spelling and biscuits!"}] + st.session_state.messages
            ).choices[0].message.content
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            speak_text(resp)
