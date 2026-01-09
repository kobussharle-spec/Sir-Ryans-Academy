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

import streamlit as st

st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑")

# THIS IS THE SAFETY VALVE
try:
    st.image("logo.png", width=300)
except:
    st.info("🏛️ Sir Ryan is currently hanging the Academy portraits. Welcome!")

st.title("Sir Ryan's Academy")

# --- 1. SETUP & HEADER ---
import streamlit as st

# Make sure this is the very first Streamlit command!
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="centered")

# --- LOGO DISPLAY ---
# Ensure your logo file (e.g., 'logo.png') is in the same GitHub folder as your script
st.image("logo.png", width=300) 

st.title("👑 Sir Ryan's Executive Academy")
st.markdown("### *Mastering English with Elocution & Etiquette*")
st.divider()

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓", layout="wide")

# --- 2. THE PERMANENT ARCHIVES ---
# DEAN: Paste your workbook text between the triple quotes!
ACADEMY_ARCHIVES = """
PASTE YOUR WORKBOOK TEXT HERE.
(Day 1 to Day 7 content)
"""

# --- 3. THE VOICE BOX ---
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

# --- HIGH-VISIBILITY SIDEBAR STYLING ---
st.markdown("""
    <style>
    /* Force Sidebar Buttons to be Oxford Blue with Gold Text at all times */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #002147 !important; /* Oxford Blue */
        color: #C5A059 !important; /* Academy Gold */
        border: 2px solid #C5A059 !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: bold !important;
        height: 3em !important;
        display: block !important;
    }

    /* Force the Link Buttons (The Library) to be visible */
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

    /* Change colour when hovering so the user knows it's active */
    [data-testid="stSidebar"] .stButton > button:hover, 
    [data-testid="stSidebar"] a:hover {
        background-color: #C5A059 !important;
        color: #002147 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "merits": 0, "gradebook": [], 
        "student_name": "Scholar", "pdf_text": ACADEMY_ARCHIVES, 
        "streak_count": 1, "last_visit": datetime.date.today(),
        "english_level": None, "welcomed": False,
        "current_subject": "Interview Prep (STAR Method)"
    })

# --- 6. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Executive Academy")
    name_input = st.text_input("Name for the Register:")
    license_key = st.text_input("License Key:", type="password")
    
    if st.button("Unlock the Study Hub"):
        # We clean the input to ignore spaces and capital letters
        clean_key = license_key.strip().lower()
        
        if name_input:
            # 1. Check for Full Access
            if clean_key == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.access_level = "Full"
                st.session_state.student_name = name_input
                st.rerun()
            
            # 2. Check for Guest Access
            elif clean_key == "guest":
                st.session_state.authenticated = True
                st.session_state.access_level = "Guest"
                st.session_state.student_name = f"{name_input} (Guest)"
                st.rerun()
                
            # 3. If neither matches
            else:
                st.error("Access Denied. Please check your License Key.")
        else:
            st.warning("Please enter your name in the Register, old sport.")
            
    st.stop()

# --- 7. THE PLACEMENT ASSESSMENT ---
# This part ONLY runs if they passed the Gatekeeper above
if st.session_state.english_level is None:
    st.title("📜 Academy Placement Evaluation")
    
    # Fast-track for the Dean and his daughter
    if st.button("🏆 Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()

    st.info(f"Welcome, {st.session_state.student_name}. Please complete your entry assessment.")
    
    with st.form("assessment"):
        # ... your questions here ...
        submitted = st.form_submit_button("Submit for Grading")
        if submitted:
            st.session_state.english_level = "Executive" # or your grading logic
            st.rerun()
            
    # CRITICAL: This stops the app here so the Main Hub doesn't show yet!
    st.stop()

# --- 8. THE HEADMASTER'S WELCOME ---
if not st.session_state.welcomed:
    welcome_msg = f"Welcome to the Academy, {st.session_state.student_name}! I see you are an {st.session_state.english_level}. I have your workbook ready. Grab a biscuit and let's begin."
    speak_text(welcome_msg)
    st.session_state.welcomed = True

# --- 9. SIDEBAR: THE ACADEMY REGISTRY ---
with st.sidebar:
    st.markdown(f"### 👤 Scholar: {st.session_state.student_name}")
    st.divider()

    # --- 📚 Study Selection ---
    st.markdown("### 📚 Study Focus")
    st.session_state.current_subject = st.selectbox("Select Focus Area:", [
        "General English", "English: Tenses & Time", "English: Grammar Mastery",
        "English: Vocabulary & Diction", "English: Pronunciation & Elocution",
        "Executive Conversation", "Business Writing & Emails", "Professional Etiquette",
        "Medical English", "Legal English", "Technical & Engineering English",
        "IELTS/TOEFL Preparation", "Interview Excellence (STAR Method)", "British Idioms & Slang"
    ])

    st.divider()

    # --- 🏛️ THE ROYAL LIBRARY (WITH ACCESS CONTROL) ---
    st.markdown("### 🏛️ The Royal Library Vault")
    
    if st.session_state.access_level == "Guest":
        st.warning("🔒 Library Restricted")
        st.write("The Royal Vault is reserved for Enrolled Scholars.")
        st.link_button("👑 Unlock Full Academy Access", "https://www.etsy.com/shop/YourShopName")
        st.button("📖 Oxford Dictionary (Locked)", disabled=True)
        st.button("📻 BBC Learning (Locked)", disabled=True)
    else:
        st.success("👑 Full Access Granted")
        
        st.write("**Dictionaries & Phonetics**")
        st.link_button("Oxford English Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("Cambridge Explanatory Dictionary", "https://dictionary.cambridge.org/dictionary/english/explanatory")
        st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
        
        st.write("**Grammar & Level Testing**")
        st.link_button("BBC Grammar Guide", "https://www.bbc.co.uk/learningenglish/english/grammar")
        st.link_button("English Level Test (EngExam)", "https://engxam.com/english-level-test/")
        st.link_button("Cambridge English Support", "https://www.cambridgeenglish.org/supporting-learners/?level=basic")
        
        st.write("**Study Resources & Games**")
        st.link_button("Oxford University Press (ELT)", "https://elt.oup.com/learning_resources/")
        st.link_button("Baamboozle Educational Games", "https://www.baamboozle.com/")
        st.link_button("ABCya! Learning Fun", "https://www.abcya.com/")
        
        st.write("**Professional Certification**")
        st.link_button("TEFL Certificate (Teacher Record)", "https://teacherrecord.com/tefl-certificate")
    
    # --- Support & Exit ---
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🧹 Reset Study Session"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='color: #C5A059; font-size: 0.8em;'>© 2026 J Steenekamp<br>Sir Ryan's Academy<br>All Rights Reserved</p>", unsafe_allow_html=True)

# --- 🏆 THE ACADEMY TROPHY CABINET ---
    st.divider()
    st.markdown("### 🏆 Your Trophy Cabinet")
    
    # Initialize the cabinet if it doesn't exist
    if "trophies" not in st.session_state:
        st.session_state.trophies = []

    if not st.session_state.trophies:
        st.info("Your cabinet is empty. Complete a lesson to earn your first trophy!")
    else:
        # Display earned trophies in a nice row
        cols = st.columns(len(st.session_state.trophies))
        for i, trophy in enumerate(st.session_state.trophies):
            with cols[i]:
                st.markdown(f"## {trophy}")
                st.caption("Well Done!")

# --- 10. MAIN HUB ---
st.markdown(f"""
<div style="border: 3px solid #C5A059; padding: 20px; border-radius: 10px; background-color: white;">
    <h3 style="color: #002147;">📜 Headmaster's Study</h3>
    <p>Good day, <b>{st.session_state.student_name}</b>. The Academy Library is fully at your disposal.</p>
    <p>We are currently prepared for <b>{st.session_state.current_subject}</b>. What shall we master today?</p>
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
                st.info(f"Sir Ryan heard: '{transcription}'")
                critique = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Critique this based on your knowledge. Mention biscuits!"},
                              {"role": "user", "content": f"Critique this: {transcription}"}]
                ).choices[0].message.content
                st.markdown(critique)
                speak_text(critique)

with col_b:
    st.subheader("📝 Quick Actions")
    if st.button("📝 Start Quiz"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, please quiz me on the workbook!"})
        st.rerun()

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
            messages=[{"role": "system", "content": f"You are Sir Ryan. Use British-isms and mention biscuits!"}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | All Rights Reserved</p></center>", unsafe_allow_html=True)
