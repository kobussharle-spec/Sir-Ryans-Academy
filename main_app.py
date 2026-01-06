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
from io import BytesIO

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# --- 2. INITIALISE ACADEMY STATE ---
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
    filename = "academy_voice.mp3"
    try:
        communicate = edge_tts.Communicate(clean_text, "en-GB-RyanNeural")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(communicate.save(filename))
        loop.close()
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.warning("Sir Ryan's voice is a bit hoarse.")

def show_welcome_letter():
    st.markdown(f"""
    ### 📜 A Personal Note from the Headmaster
    **To the Honourable {st.session_state.student_name},**
    It is with great pride that I welcome you to **Sir Ryan's Academy**. We shall pursue knowledge with the utmost **honour**.
    """)
    st.divider()

# --- 4. THE SECURITY GATE ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Academy")
    
    # Ask for name and key in the SAME section
    name_input = st.text_input("Please enter your name for the register:", key="login_name")
    password_input = st.text_input("Enter the Academy License Key:", type="password", key="login_pass")
    
    if st.button("Unlock the Study Hub"):
        if password_input == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.success("The gates are opening... Welcome, old sport!")
            time.sleep(1) # A small pause for effect
            st.rerun()  # THIS IS THE CRITICAL LINE
        else:
            st.error("I'm afraid that key doesn't fit the lock, or you forgot your name.")
    
    st.stop() # This ensures NOTHING else (like the letter) shows until logged in

# --- 5. THE ACADEMY SIDEBAR (All-In-One) ---
with st.sidebar:
    st.title("🏫 Academy Controls")
    
    st.header("📜 Student Gradebook")
    if not st.session_state.gradebook:
        st.write("No grades recorded yet.")
    else:
        st.table(pd.DataFrame(st.session_state.gradebook))

    st.divider()
    st.header("📚 Subject Registry")
    subject = st.selectbox("Select the field of study:", [
        "English: Grammar", "English: Vocabulary", "English: Conversation", 
        "English: Business English", "Medicine", "Law"
    ], key="master_subject_selector")
    st.session_state.current_subject = subject

    st.header("📄 Study Materials")
    uploaded_file = st.file_uploader("Upload your PDF notes:", type="pdf")

    if st.button("📜 Start Formal Assessment", key="exam_hall_btn"):
        if not uploaded_file:
            st.warning("Upload materials first, old sport!")
        else:
            st.session_state.gradebook.append({"Subject": subject, "Student": st.session_state.student_name, "Grade": "In Progress..."})
            st.info("Exam initialised in the Main Hall!")

    st.divider()
    st.markdown(f"🔥 **Study Streak:** {st.session_state.streak_count} Days")
    
    with st.expander("📕 Quick Dictionary"):
        word = st.text_input("Look up a word:").strip()
        if word:
            resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if resp.status_code == 200:
                st.write(resp.json()[0]['meanings'][0]['definitions'][0]['definition'])
    
    st.sidebar.caption("© 2026 Sir Ryan's Academy | Established with Honour")

# --- 6. MAIN CLASSROOM ---
show_welcome_letter()

if st.session_state.english_level is None:
    st.subheader("Placement Evaluation")
    lvl = st.radio("Choose your level:", ["Beginner", "Intermediate", "Advanced"], horizontal=True)
    if st.button("Confirm Level"):
        st.session_state.english_level = lvl
        st.rerun()
    st.stop()

# Chat Hub
st.write(f"### ⚡ Current Lesson: {subject}")
if prompt := st.chat_input("Ask Sir Ryan anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. The subject is {subject}."}] + st.session_state.messages,
        )
        response = completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        speak_text(response)

st.caption("Sir Ryan's Academy - Excellence in English & Beyond")
