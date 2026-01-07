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

# --- 2. THE PERMANENT ACADEMY ARCHIVES ---
# PASTE YOUR WORKBOOK TEXT BETWEEN THE TRIPLE QUOTES BELOW
ACADEMY_ARCHIVES = """
PASTE YOUR TEXT HERE
"""

# --- 3. EXECUTIVE THEME ---
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
    }
    footer {visibility: hidden;} /* Hides Streamlit's default footer to keep it Executive */
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "merits": 0, "gradebook": [], 
        "student_name": "Scholar", "pdf_text": ACADEMY_ARCHIVES, 
        "streak_count": 1, "last_visit": datetime.date.today(),
        "current_subject": "Interview Prep (STAR Method)"
    })

# --- 5. THE GATEKEEPER ---
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

# --- 6. VOICE ENGINE ---
def speak_text(text):
    try:
        clean = text.replace("**", "").replace("#", "").replace("_", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        ts = str(int(time.time()))
        filename = f"v_{ts}.mp3"
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 7. SIDEBAR (With Copyright) ---
with st.sidebar:
    st.title("🏫 Academy Registry")
    st.session_state.current_subject = st.selectbox("Select Study Focus:", [
        "English: Tenses", "English: Grammar", "English: Pronunciation",
        "English: Vocabulary", "English: Conversation", 
        "English: Writing - Emails", "English: Writing - Reports",
        "Preparing for ELS", "Interview Prep (STAR Method)", "Business English", 
        "Medicine", "Law", "General Knowledge"
    ])

    with st.expander("📖 Academy User Manual"):
        st.write("Sir Ryan has memorised your workbook! Simply ask him questions or request a quiz.")

    with st.expander("📕 Academy Dictionary"):
        word = st.text_input("Look up a word:").strip()
        if word:
            try:
                res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
                if res.status_code == 200:
                    st.write(f"**Def:** {res.json()[0]['meanings'][0]['definitions'][0]['definition']}")
            except: st.error("Dictionary offline.")

    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    st.markdown("---")
    st.markdown("### 📜 Legal & Honour")
    st.write("© 2026 J Steenekamp")
    st.write("All Rights Reserved")
    
    if st.button("🧹 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- 8. MAIN HUB ---
st.markdown(f"<h1 style='color: #002147;'>🎓 Sir Ryan’s Executive Academy</h1>", unsafe_allow_html=True)

st.markdown(f"""
<div style="border: 3px solid #C5A059; padding: 20px; border-radius: 10px; background-color: white;">
    <h3 style="color: #002147;">📜 A Note from the Headmaster</h3>
    <p>Welcome, <b>{st.session_state.student_name}</b>. Shall we begin with <b>{st.session_state.current_subject}</b>?</p>
    <p>Please, have a <b>biscuit</b> and let us proceed.</p>
    <p style='text-align: right; font-size: 0.8em; color: #888;'>© 2026 J Steenekamp | Sir Ryan's Executive Academy</p>
</div>
""", unsafe_allow_html=True)

with col_a:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    
    if rec: 
        st.audio(rec['bytes'])
        if st.button("Submit for Headmaster's Critique"):
            with st.spinner("Sir Ryan is listening closely..."):
                try:
                    # 1. Save the audio temporarily
                    with open("student_response.wav", "wb") as f:
                        f.write(rec['bytes'])
                    
                    # 2. Transcribe using Groq's Whisper "Ears"
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    with open("student_response.wav", "rb") as audio_file:
                        transcription = client.audio.transcriptions.create(
                            file=("student_response.wav", audio_file.read()),
                            model="whisper-large-v3",
                            response_format="text"
                        )
                    
                    # 3. Sir Ryan provides his feedback
                    st.info(f"Sir Ryan heard: '{transcription}'")
                    
                    critique = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": f"You are Sir Ryan. Critically evaluate this student's spoken answer based on the STAR method and your workbook knowledge: {st.session_state.pdf_text[:4000]}. Be posh, encouraging, and mention biscuits!"},
                            {"role": "user", "content": f"I said: {transcription}. How was my content and clarity?"}
                        ]
                    ).choices[0].message.content
                    
                    st.markdown(critique)
                    speak_text(critique) # Sir Ryan speaks his feedback!
                    st.session_state.gradebook.append({"Subject": "Oral Exam", "Grade": "Graded"})
                    st.success("Examination recorded in your Gradebook!")
                except Exception as e:
                    st.error(f"A spot of bother with the ears: {e}")

st.divider()
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Use this text as knowledge: {st.session_state.pdf_text[:8000]}. Use British-isms and mention biscuits!"}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

# --- 9. THE PERMANENT FOOTER ---
st.markdown("<br><br><br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Executive Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
