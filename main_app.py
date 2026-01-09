# --- 1. THE FACULTY (IMPORTS) ---
import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime

# --- 2. THE FOUNDATION (MUST BE FIRST) ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 3. THE GRAND ENTRANCE (LOGO) ---
try:
    st.image("logo.png", width=250)
except:
    st.info("🏛️ The Academy crest is being polished. Welcome!")

st.title("👑 Sir Ryan's Executive Academy")
st.markdown("### *Mastering English with Elocution & Etiquette*")
st.divider()

# --- 4. SESSION STATES (The Academy Register) ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "merits": 0, "student_name": "Scholar",
        "english_level": None, "welcomed": False, "access_level": "None",
        "current_subject": "General English", "trophies": []
    })

# --- 5. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.subheader("🏛️ Please sign the Register to enter")
    name = st.text_input("Full Name:")
    key = st.text_input("License Key:", type="password")
    if st.button("Unlock Study Hub"):
        if name and key.lower().strip() == "oxford2026":
            st.session_state.authenticated = True
            st.session_state.access_level = "Full"
            st.session_state.student_name = name
            st.rerun()
        elif name and key.lower().strip() == "guest":
            st.session_state.authenticated = True
            st.session_state.access_level = "Guest"
            st.session_state.student_name = f"{name} (Guest)"
            st.rerun()
        else:
            st.error("Access Denied. Check your key, old sport.")
    st.stop()

# --- 6. VOICE ENGINE ---
def speak_text(text):
    try:
        clean = text.replace("**", "").replace("#", "").replace("_", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        filename = f"voice_{int(time.time())}.mp3"
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 7. THE SIDEBAR (REBUILT & ORGANISED) ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.student_name}")
    st.markdown(f"**Access:** {st.session_state.access_level}")
    st.divider()
    
    # RESTORED SUBJECT LIST
    st.markdown("### 📚 Study Focus")
    subjects = [
        "General English", "English: Tenses & Time", "English: Grammar Mastery",
        "English: Vocabulary & Diction", "English: Pronunciation & Elocution",
        "Executive Conversation", "Business Writing & Emails", "Professional Etiquette",
        "Medical English", "Legal English", "Technical & Engineering English",
        "IELTS/TOEFL Preparation", "Interview Excellence (STAR Method)", "British Idioms & Slang"
    ]
    st.session_state.current_subject = st.selectbox("Current Lesson:", subjects)
    
    st.divider()
    st.markdown("### 🏛️ The Royal Library")
    if st.session_state.access_level == "Full":
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("Phonetic Tool", "https://phonetic-spelling.com/")
    else:
        st.warning("🔒 Library restricted to Full Scholars.")
        st.link_button("👑 Get Full Access", "https://www.etsy.com")

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🧹 Reset Academy Session"):
        st.session_state.clear()
        st.rerun()

# --- 8. MAIN HUB ---
st.info(f"Currently Studying: **{st.session_state.current_subject}**")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit for Critique"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            transcript = client.audio.transcriptions.create(file=("audio.wav", rec['bytes']), model="whisper-large-v3", response_format="text")
            st.write(f"*Sir Ryan heard:* {transcript}")
            # Posh Critique logic here
            resp = "Top-notch effort! Have a biscuit."
            st.markdown(resp)
            speak_text(resp)

with col2:
    st.subheader("📝 Quick Actions")
    if st.button("📝 Start Knowledge Quiz"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, please quiz me!"})
        st.rerun()

st.divider()
# --- 9. CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask the Headmaster..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "You are Sir Ryan, a posh British tutor. Be encouraging and mention biscuits!"}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        speak_text(response)
