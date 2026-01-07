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

# --- 6. THE EXECUTIVE ASSESSMENT TEST ---
if st.session_state.get("english_level") is None:
    st.markdown("## 📜 Academy Placement Evaluation")
    st.info(f"Welcome, {st.session_state.student_name}. Before we begin, Sir Ryan must assess your current standing.")
    
    with st.form("assessment_form"):
        st.write("---")
        q1 = st.radio("1. Which sentence is grammatically correct for a formal report?", 
                    ["I done the task yesterday.", "I have completed the task yesterday.", "I completed the task yesterday."])
        
        q2 = st.radio("2. In the STAR method, what does the 'R' stand for?", 
                    ["Review", "Results", "Reaction", "Reasoning"])
        
        q3 = st.selectbox("3. Choose the most professional synonym for 'Happy':", 
                        ["Chuffed", "Satisfied", "Content", "Delighted"])
        
        submit_test = st.form_submit_button("Submit for Grading")
        
        if submit_test:
            # Simple Logic to determine level
            score = 0
            if q1 == "I completed the task yesterday.": score += 1
            if q2 == "Results": score += 1
            if q3 == "Delighted": score += 1
            
            if score == 3:
                st.session_state.english_level = "Advanced Executive"
                st.session_state.merits += 50
            elif score == 2:
                st.session_state.english_level = "Intermediate Scholar"
                st.session_state.merits += 20
            else:
                st.session_state.english_level = "Beginner Professional"
            
            st.success(f"Grading Complete! You have been placed in: {st.session_state.english_level}")
            time.sleep(2)
            st.rerun()
    st.stop() # Stops the rest of the app from loading until test is done

# --- 7. THE HEADMASTER'S WELCOME (Triggers once per login) ---
if "welcomed" not in st.session_state:
    welcome_text = f"""
    Welcome to the Academy, {st.session_state.student_name}! 
    I see you have been placed in the {st.session_state.english_level} tier. 
    I have your workbook ready in the archives. Shall we get to work on your career 
    success? Do grab a biscuit and let's begin!
    """
    # Sir Ryan speaks the welcome
    speak_text(welcome_text)
    
    # Show a temporary celebratory message
    st.toast(f"Headmaster Ryan is chuffed to see you, {st.session_state.student_name}!", icon="🎓")
    
    # Ensure he doesn't repeat this every time the page refreshes
    st.session_state.welcomed = True

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
    # This captures the audio directly from your microphone
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    
    if rec: 
        # 1. Play the audio back to the student immediately
        st.audio(rec['bytes'])
        
        # 2. Use the 'bytes' from the recorder directly for the Headmaster
        if st.button("Submit for Headmaster's Critique"):
            with st.spinner("Sir Ryan is listening closely..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # We send the bytes directly to Sir Ryan's "Ears" (Whisper)
                    # We name it 'audio.wav' so the system knows the format
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", rec['bytes']),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    
                    # Show the student what was heard
                    st.info(f"Sir Ryan heard: '{transcription}'")
                    
                    # Sir Ryan evaluates the text against your Workbook
                    critique = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": f"You are Sir Ryan. Evaluate this transcript based on your STAR method workbook: {st.session_state.pdf_text[:4000]}. Be posh and mention biscuits!"},
                            {"role": "user", "content": f"Critique my answer: {transcription}"}
                        ]
                    ).choices[0].message.content
                    
                    st.markdown(critique)
                    speak_text(critique) # Sir Ryan speaks his feedback
                    st.session_state.gradebook.append({"Subject": "Oral", "Grade": "Graded"})
                    
                except Exception as e:
                    st.error(f"A spot of bother with the ears: {e}")
    else:
        st.caption("Click 'Record' to begin your examination, old sport.")
        
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
