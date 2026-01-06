import streamlit as st
from groq import Groq
import PyPDF2
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import random
import requests
import urllib.parse
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# --- 2. INITIALISE ALL STATES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "student_name" not in st.session_state:
    st.session_state.student_name = "Scholar"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gradebook" not in st.session_state:
    st.session_state.gradebook = []
if "english_level" not in st.session_state:
    st.session_state.english_level = None
if "vocab_bank" not in st.session_state:
    st.session_state.vocab_bank = []
if "homework_history" not in st.session_state:
    st.session_state.homework_history = []
if "merits" not in st.session_state:
    st.session_state.merits = 0
if "graduated" not in st.session_state:
    st.session_state.graduated = False
if "homework_task" not in st.session_state:
    st.session_state.homework_task = None
if "streak_count" not in st.session_state:
    st.session_state.streak_count = 1
if "last_visit_date" not in st.session_state:
    st.session_state.last_visit_date = datetime.date.today()

# --- 3. HELPER FUNCTIONS ---
def speak_text(text):
    clean_text = text.replace("**", "").replace(":", ".").replace("_", "").replace("#", "")
    try:
        communicate = edge_tts.Communicate(clean_text, "en-GB-RyanNeural")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(communicate.save("voice.mp3"))
        loop.close()
        with open("voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def show_welcome_letter():
    with st.expander("📩 Open your Welcome Letter", expanded=True):
        st.markdown(f"""
        ### 📜 A Personal Note from the Headmaster
        **To the Honourable {st.session_state.student_name},**
        Welcome to **Sir Ryan's Academy**. We shall pursue knowledge with the utmost **honour**. 
        Enjoy a **biscuit** and begin your studies below!
        """)

# --- 4. THE SECURITY GATE ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Academy")
    name_in = st.text_input("Name for Register:", key="gate_name")
    pass_in = st.text_input("License Key:", type="password", key="gate_pass")
    if st.button("Unlock the Study Hub"):
        if pass_in == "Oxford2026" and name_in:
            st.session_state.authenticated = True
            st.session_state.student_name = name_in
            st.rerun()
        else:
            st.error("I'm afraid that key doesn't fit the lock.")
    st.stop()

# --- 5. THE ACADEMY SIDEBAR (RESTORING ALL INFO) ---
with st.sidebar:
    st.title("🏫 Academy Controls")
    
    st.header("📜 Gradebook")
    if not st.session_state.gradebook: st.write("No grades yet.")
    else: st.table(pd.DataFrame(st.session_state.gradebook))

    st.divider()
    subject = st.selectbox("Subject Registry:", ["English: Grammar", "Medicine", "Law", "Business English"])
    uploaded_file = st.file_uploader("Upload PDF:", type="pdf")
    
    if st.button("📜 Start Formal Assessment"):
        st.session_state.gradebook.append({"Subject": subject, "Student": st.session_state.student_name, "Grade": "In Progress..."})
        st.toast("Examination Hall is ready!")

    st.divider()
    # RESTORED SIDEBAR TOOLS
    st.info(f"🔥 Streak: {st.session_state.streak_count} Days")
    try:
        weather = requests.get("https://wttr.in/London?format=%c+%t").text
        st.write(f"🇬🇧 London Weather: {weather}")
    except: pass
    
    with st.expander("📕 Quick Dictionary"):
        d_word = st.text_input("Lookup:")
        if d_word:
            r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{d_word}")
            if r.status_code == 200: st.write(r.json()[0]['meanings'][0]['definitions'][0]['definition'])

    st.sidebar.caption("© 2026 Sir Ryan's Academy")

# --- 6. MAIN HUB (RESTORING ALL BUTTONS) ---
show_welcome_letter()

# QUICK ACTION BUTTONS
st.write("### ⚡ Quick Actions")
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("📝 Start Quiz"): st.session_state.messages.append({"role":"user", "content":"Give me a quick quiz!"})
with c2: 
    if st.button("📚 New Homework"): st.session_state.homework_task = "Explain the difference between 'Your' and 'You're'."
with c3: 
    if st.button("🏆 View Merits"): st.toast(f"Merits: {st.session_state.merits}")

if st.session_state.homework_task:
    st.warning(f"**Homework:** {st.session_state.homework_task}")

st.divider()

# CHAT INTERFACE
if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        comp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Sir Ryan, a posh British tutor."}] + st.session_state.messages,
        )
        ans = comp.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        speak_text(ans)
