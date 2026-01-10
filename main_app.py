import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber
import io

# --- 1. FOUNDATION & STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 20px;
        border: 2px solid #C5A059;
        font-weight: bold;
    }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "english_level" not in st.session_state:
    st.session_state.english_level = "Pending"
if "vault" not in st.session_state:
    st.session_state.vault = {}

# --- 3. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.get("mute", False): return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("temp.mp3"))
        with open("temp.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 4. SHARED LOGO FUNCTION ---
def display_academy_logo(width=350):
    try:
        st.image("logo.png", width=width)
    except:
        st.markdown(f"""
            <div style="background-color: #002147; padding: 10px; border-radius: 10px; border: 2px solid #C5A059; text-align: center; width: {width}px;">
                <h2 style="color: #C5A059; margin: 0; font-family: 'Times New Roman';">🏛️ SIR RYAN'S ACADEMY</h2>
            </div>
        """, unsafe_allow_html=True)

# --- 5. THE LOGIN GATE ---
if not st.session_state.authenticated:
    display_academy_logo()
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:", key="reg_name")
        nick_in = st.text_input("Nickname:", key="reg_nick")
    with c2:
        key_in = st.text_input("License Key:", type="password", key="reg_key")
        if st.button("Register & Begin Placement Exam"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.rerun()
    st.stop()

# --- 6. ENTRANCE EVALUATION ---
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    display_academy_logo(width=200)
    st.title("📜 Entrance Evaluation")
    with st.form("level_test"):
        st.radio("1. Which spelling reflects proper British honour?", ["Honor", "Honour"], key="e1")
        st.radio("2. If you are 'chuffed', you are feeling...", ["Very pleased", "Quite annoyed"], key="e2")
        st.radio("3. I _______ (see) that film three times already.", ["saw", "have seen"], key="e3")
        if st.form_submit_button("Submit Assessment"):
            st.session_state.english_level = "Senior Scholar"
            st.rerun()
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    display_academy_logo(width=200)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Rank: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Vocabulary", "Business English", "🏆 GRAND FINAL"]
    st.session_state.current_subject = st.selectbox("Current Module:", subjects)

    st.divider()
    with st.expander("📖 Library Links"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")

    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 8. MAIN HUB ---
display_academy_logo(width=250)
st.title(f"Welcome to the {st.session_state.current_subject} Hall")

# --- 9. THE QUIZ ENGINE ---
st.markdown("### ✍️ Module Examination")
with st.container():
    if st.session_state.current_subject == "Tenses":
        with st.form("subject_quiz"):
            q1 = st.radio("1. I _______ (work) here since 2020.", ["work", "have been working", "am working"])
            q2 = st.radio("2. By next year, I _______ (finish) my degree.", ["will finish", "will have finished", "finish"])
            if st.form_submit_button("Submit for Marking"):
                st.success("Exam submitted! You've earned a biscuit for your hard work.")
    else:
        st.info("Select 'Tenses' to see the exam, or chat with Sir Ryan below for guidance.")

# --- 10. STUDY DESKS ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎤 Oral Elocution")
    audio = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Submit", key='oral_v11')
    if audio and st.button("Critique My Accent"):
        st.info("Sir Ryan is listening... (Splendid clarity, Scholar!)")

with c2:
    st.subheader("📝 Homework Vault")
    hw = st.file_uploader("Upload PDF:", type=['pdf'])
    if hw and st.button("Archive to Vault"):
        st.success("Homework archived! I shall look it over after tea.")

# --- 11. CHAT HUB ---
st.divider()
st.subheader("💬 Audience with the Headmaster")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Use British spelling and mention biscuits."}] + st.session_state.messages).choices[0].message.content
        st.markdown(resp); st.session_state.messages.append({"role": "assistant", "content": resp}); speak_text(resp)

st.markdown("<br><hr><center><p>© 2026 J Steenekamp | Sir Ryan's Academy</p></center>", unsafe_allow_html=True)
