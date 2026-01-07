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
        # CHECK THIS LINE BELOW CAREFULLY:
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.rerun()

# --- 7. THE PLACEMENT ASSESSMENT (General English Edition) ---
if st.session_state.english_level is None:
    st.title("📜 Academy Placement Evaluation")
    st.info(f"Welcome, {st.session_state.student_name}. Please complete this brief English evaluation to help Sir Ryan tailor your experience.")
    
    with st.form("assessment"):
        st.write("### Part 1: Formal Correspondence")
        q1 = st.radio("1. Which of these is the most professional way to start an email to someone you've never met?", 
                    ["Hey there!", "To whom it may concern,", "Hiya!"])
        
        st.write("### Part 2: Grammar & Tense")
        q2 = st.radio("2. Choose the correct sentence for a past achievement:", 
                    ["I have lead the team last year.", "I led the team last year.", "I leaded the team last year."])
        
        st.write("### Part 3: Executive Vocabulary")
        q3 = st.radio("3. If a meeting is 'adjourned', what has happened?", 
                    ["It has started.", "It has been cancelled.", "It has ended for the time being."])
        
        if st.form_submit_button("Submit for Grading"):
            # Grading Logic
            score = 0
            if q1 == "To whom it may concern,": score += 1
            if q2 == "I led the team last year.": score += 1
            if q3 == "It has ended for the time being.": score += 1
            
            levels = {3: "Advanced Executive", 2: "Intermediate Scholar", 1: "Beginner Professional", 0: "Beginner Professional"}
            st.session_state.english_level = levels[score]
            st.success(f"Grading Complete! Sir Ryan has placed you in the: {st.session_state.english_level} tier.")
            time.sleep(2)
            st.rerun()
    st.stop()

# --- 8. THE HEADMASTER'S WELCOME ---
if not st.session_state.welcomed:
    welcome_msg = f"Welcome to the Academy, {st.session_state.student_name}! I see you are an {st.session_state.english_level}. I have your workbook ready. Grab a biscuit and let's begin."
    speak_text(welcome_msg)
    st.session_state.welcomed = True

# --- 9. SIDEBAR: THE ACADEMY REGISTRY ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/graduation-cap.png", width=80)
    st.title("🏫 Academy Registry")
    
    st.markdown("### 👤 Scholar Profile")
    st.write(f"**Name:** {st.session_state.student_name}")
    st.write(f"**Status:** {st.session_state.english_level}")
    st.write(f"**Merits:** ⭐ {st.session_state.merits}")
    
    st.divider()
    
    # --- Study Selection ---
    st.markdown("### 📚 Study Focus")
    st.session_state.current_subject = st.selectbox("Select Focus Area:", [
        "General English", "English: Tenses & Time", "English: Grammar Mastery",
        "English: Vocabulary & Diction", "English: Pronunciation & Elocution",
        "Executive Conversation", "Business Writing & Emails", "Professional Etiquette",
        "Medical English", "Legal English", "Technical & Engineering English",
        "IELTS/TOEFL Preparation", "Interview Excellence (STAR Method)", "British Idioms & Slang"
    ])

    st.divider()

    # --- THE ROYAL LIBRARY (DIRECT LINKS - NO HIDING!) ---
    st.markdown("### 🏛️ The Royal Library Vault")
    
    st.write("**Dictionaries & Phonetics**")
    st.link_button("Oxford English Dictionary", "https://www.oed.com/?tl=true")
    st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/dictionary/english/explanatory")
    st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
    
    st.write("**Exam & Level Testing**")
    st.link_button("English Level Test", "https://engxam.com/english-level-test/")
    st.link_button("TEFL Certification Info", "https://teacherrecord.com/tefl-certificate")
    
    st.write("**Study Resources**")
    st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish/english/grammar")
    st.link_button("Oxford University Press", "https://elt.oup.com/learning_resources/")
    
    st.write("**Interactive Games**")
    st.link_button("Baamboozle Games", "https://www.baamboozle.com/")
    st.link_button("ABCya Hub", "https://www.abcya.com/")

    st.divider()
    
    # --- Support & Exit ---
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🧹 Reset Study Session"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='color: #C5A059; font-size: 0.8em;'>© 2026 J Steenekamp<br>Sir Ryan's Academy<br>All Rights Reserved</p>", unsafe_allow_html=True)

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
