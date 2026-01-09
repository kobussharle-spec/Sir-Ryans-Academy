# --- 1. THE FACULTY (IMPORTS) ---
import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import requests

# --- 2. THE FOUNDATION (CONFIG) ---
# This must be the absolute first Streamlit command
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="centered")

# --- 3. THE GRAND ENTRANCE (LOGO & HEADER) ---
try:
    # This tries to show your logo. If the file is missing, it won't crash the app.
    st.image("logo.png", width=300)
except:
    st.info("🏛️ Sir Ryan is currently polishing the Academy portraits. Welcome!")

st.title("👑 Sir Ryan's Executive Academy")
st.markdown("### *Mastering English with Elocution & Etiquette*")
st.divider()

# --- 4. THE PERMANENT ARCHIVES ---
# DEAN: You can paste your Day 1 to Day 7 text here later!
ACADEMY_ARCHIVES = """
Welcome to the Academy Workbook.
"""

# --- 5. THE VOICE BOX ---
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
    except:
        pass

# --- 6. HIGH-VISIBILITY SIDEBAR STYLING ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stButton > button {
        background-color: #002147 !important;
        color: #C5A059 !important;
        border: 2px solid #C5A059 !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] a {
        background-color: #002147 !important;
        color: #C5A059 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        display: block !important;
        margin-bottom: 8px !important;
        text-align: center !important;
        border: 1px solid #C5A059 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 7. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "merits": 0, "gradebook": [], 
        "student_name": "Scholar", "pdf_text": ACADEMY_ARCHIVES, 
        "streak_count": 1, "last_visit": datetime.date.today(),
        "english_level": None, "welcomed": False,
        "current_subject": "General English",
        "access_level": "None", "trophies": []
    })

# --- 8. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to the Register")
    name_input = st.text_input("Name for the Register:")
    license_key = st.text_input("License Key:", type="password")
    
    if st.button("Unlock the Study Hub"):
        clean_key = license_key.strip().lower()
        if name_input:
            if clean_key == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.access_level = "Full"
                st.session_state.student_name = name_input
                st.rerun()
            elif clean_key == "guest":
                st.session_state.authenticated = True
                st.session_state.access_level = "Guest"
                st.session_state.student_name = f"{name_input} (Guest)"
                st.rerun()
            else:
                st.error("Access Denied. Please check your License Key.")
        else:
            st.warning("Please enter your name, old sport.")
    st.stop()

# --- 9. THE PLACEMENT ASSESSMENT ---
if st.session_state.english_level is None:
    st.title("📜 Academy Placement Evaluation")
    if st.button("🏆 Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    st.stop()

# --- 10. SIDEBAR: THE ACADEMY REGISTRY ---
with st.sidebar:
    st.markdown(f"### 👤 Scholar: {st.session_state.student_name}")
    st.divider()
    st.markdown("### 📚 Study Focus")
    st.session_state.current_subject = st.selectbox("Select Focus:", [
        "General English", "Executive Conversation", "Business Writing", "British Idioms"
    ])
    st.divider()
    st.markdown("### 🏛️ Library Vault")
    if st.session_state.access_level == "Guest":
        st.link_button("👑 Unlock Full Access", "https://www.etsy.com/shop/YourShopName")
    else:
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Grammar", "https://www.bbc.co.uk/learningenglish/english/grammar")
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🧹 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- 11. MAIN HUB & ORAL EXAM ---
st.markdown(f"""
<div style="border: 3px solid #C5A059; padding: 20px; border-radius: 10px; background-color: white;">
    <h3 style="color: #002147;">📜 Headmaster's Study</h3>
    <p>Good day, <b>{st.session_state.student_name}</b>. We are ready for <b>{st.session_state.current_subject}</b>.</p>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec: 
        st.audio(rec['bytes'])
        if st.button("Submit for Critique"):
            with st.spinner("Sir Ryan is listening..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                transcription = client.audio.transcriptions.create(file=("audio.wav", rec['bytes']), model="whisper-large-v3", response_format="text")
                critique = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "You are Sir Ryan. Critique this. Mention biscuits!"},
                              {"role": "user", "content": f"Critique this: {transcription}"}]
                ).choices[0].message.content
                st.markdown(critique)
                speak_text(critique)

with col_b:
    st.subheader("📝 Quick Actions")
    if st.button("📝 Start Quiz"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, please quiz me on the workbook!"})
        st.rerun()

# --- 12. CHAT INTERFACE ---
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
            messages=[{"role": "system", "content": "You are Sir Ryan. Use British-isms and biscuits!"}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)
