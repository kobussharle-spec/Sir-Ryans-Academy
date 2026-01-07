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

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓", layout="wide")

# --- 2. THE PERMANENT ARCHIVES ---
# DEAN: Paste your workbook text between the triple quotes!
ACADEMY_ARCHIVES = """
PASTE YOUR WORKBOOK TEXT HERE.
(Day 1 to Day 7 content)
"""

# --- 3. THE VOICE BOX (Defined early to prevent NameErrors) ---
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

# --- 4. EXECUTIVE THEME ---
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
    footer {visibility: hidden;}
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
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.rerun()
        else: st.error("Access Denied, old sport.")
    st.stop()

# --- 7. THE PLACEMENT ASSESSMENT ---
if st.session_state.english_level is None:
    st.title("📜 Academy Placement Evaluation")
    st.info(f"Welcome, {st.session_state.student_name}. Please complete your entry assessment.")
    with st.form("assessment"):
        q1 = st.radio("1. Which is correct for a formal email?", ["I'll talk to ya later.", "I look forward to hearing from you.", "Give me a shout soon."])
        q2 = st.radio("2. In STAR, what does 'S' stand for?", ["Summary", "Situation", "Solution"])
        q3 = st.radio("3. Professional word for 'Job'?", ["Gig", "Occupation", "Work-thingy"])
        if st.form_submit_button("Submit for Grading"):
            score = (q1 == "I look forward to hearing from you.") + (q2 == "Situation") + (q3 == "Occupation")
            levels = {3: "Advanced Executive", 2: "Intermediate Scholar", 1: "Beginner Professional", 0: "Beginner Professional"}
            st.session_state.english_level = levels[score]
            st.success(f"Grading Complete! Placement: {st.session_state.english_level}")
            time.sleep(1)
            st.rerun()
    st.stop()

# --- 8. THE HEADMASTER'S WELCOME (Now speak_text is safe!) ---
if not st.session_state.welcomed:
    welcome_msg = f"Welcome to the Academy, {st.session_state.student_name}! I see you are an {st.session_state.english_level}. I have your workbook ready. Grab a biscuit and let's begin."
    speak_text(welcome_msg)
    st.session_state.welcomed = True

# --- 9. SIDEBAR ---
with st.sidebar:
    st.title("🏫 Academy Registry")
    st.write(f"**Scholar:** {st.session_state.student_name}")
    st.write(f"**Level:** {st.session_state.english_level}")
    st.divider()
    st.session_state.current_subject = st.selectbox("Select Study Focus:", [
        "Interview Prep (STAR Method)", "Business English", "English: Grammar", "English: Writing", "Medicine", "Law"
    ])
    
    with st.expander("📕 Dictionary"):
        word = st.text_input("Look up a word:").strip()
        if word:
            try:
                res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
                if res.status_code == 200:
                    st.write(f"**Def:** {res.json()[0]['meanings'][0]['definitions'][0]['definition']}")
            except: st.error("Offline.")

    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    st.markdown("---")
    st.write("© 2026 J Steenekamp | All Rights Reserved")

# --- 10. MAIN HUB ---
st.markdown(f"<h1 style='color: #002147;'>🎓 Sir Ryan’s Executive Academy</h1>", unsafe_allow_html=True)

st.markdown(f"""
<div style="border: 3px solid #C5A059; padding: 20px; border-radius: 10px; background-color: white;">
    <h3 style="color: #002147;">📜 Headmaster's Study</h3>
    <p>Good day, <b>{st.session_state.student_name}</b>. We are focusing on <b>{st.session_state.current_subject}</b> today.</p>
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
                    messages=[{"role": "system", "content": f"You are Sir Ryan, a posh British tutor. Critique this based on: {st.session_state.pdf_text[:4000]}. Mention biscuits!"},
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
            model="llama-3.1
