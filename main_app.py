import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. LOGO ---
try:
    st.image("logo.png", width=350)
except:
    st.info("🏛️ The Academy crest is being polished. Welcome!")

# --- 3. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "test_score": 0,
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0},
        "access_level": "Guest"
    })

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name_input = st.text_input("Full Name:")
        nick_input = st.text_input("Nickname:")
        user_photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with col2:
        key_input = st.text_input("License Key:", type="password")
        if st.button("Register & Proceed to Entrance Exam"):
            if name_input and key_input.lower().strip() in ["oxford2026", "guest"]:
                st.session_state.authenticated = True
                st.session_state.access_level = "Full" if key_input.lower().strip() == "oxford2026" else "Guest"
                st.session_state.student_name = name_input
                st.session_state.nickname = nick_input if nick_input else name_input
                st.session_state.avatar = user_photo
                st.session_state.english_level = "Pending"
                st.rerun()
    st.stop()

# --- 5. THE EXAMINATION ROOM ---
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    st.title("📜 Academy Entrance Evaluation")
    if st.button("🏆 Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()

    with st.form("level_test"):
        st.subheader("Placement Exam (10 Questions)")
        q1 = st.radio("1. I _______ to London last year.", ["go", "went", "have gone", "was go"])
        q2 = st.radio("2. Which is correct?", ["He don't like tea", "He doesn't like tea", "He not like tea"])
        q3 = st.radio("3. If I _______ the lottery, I would buy a castle.", ["win", "won", "will win"])
        q4 = st.radio("4. Choose the formal word:", ["Get", "Receive", "Snag"])
        q5 = st.radio("5. 'Look forward to' is followed by:", ["see you", "seeing you", "saw you"])
        q6 = st.radio("6. Which is a British spelling?", ["Color", "Colour", "Colur"])
        q7 = st.radio("7. She _______ English since 2010.", ["studies", "has been studying", "is studying"])
        q8 = st.radio("8. 'To be chuffed' means:", ["To be angry", "To be very pleased", "To be tired"])
        q9 = st.radio("9. Formal greeting for a stranger:", ["Hiya", "Dear Sir/Madam", "Hey there"])
        q10 = st.radio("10. A _______ of biscuits.", ["packet", "bunch", "flock"])
        
        if st.form_submit_button("Submit Exam & Enter Hub"):
            score = 0
            if q1 == "went": score += 1
            if q2 == "He doesn't like tea": score += 1
            if q3 == "won": score += 1
            if q4 == "Receive": score += 1
            if q5 == "seeing you": score += 1
            if q6 == "Colour": score += 1
            if q7 == "has been studying": score += 1
            if q8 == "To be very pleased": score += 1
            if q9 == "Dear Sir/Madam": score += 1
            if q10 == "packet": score += 1
            
            if score <= 4: st.session_state.english_level = "Beginner"
            elif score <= 8: st.session_state.english_level = "Intermediate"
            else: st.session_state.english_level = "Advanced Executive"
            st.rerun()
    st.stop()

# --- 6. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.mute: return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("temp.mp3"))
        with open("temp.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 7. SIDEBAR (RESTORED LINKS & WHATSAPP) ---
with st.sidebar:
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.rerun()

    st.divider()
    st.markdown("### 📚 Subject Selection")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep"]
    st.selectbox("Focus Area:", subjects, key="current_subject")

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 Dictionaries & Reference"):
        st.link_button("Oxford English Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("Cambridge Explanatory Dictionary", "https://dictionary.cambridge.org/dictionary/english/explanatory")
        st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
        st.link_button("BBC Grammar Guide", "https://www.bbc.co.uk/learningenglish/english/grammar")
        st.link_button("English Level Test", "https://engxam.com/english-level-test/")
        st.link_button("TEFL Certificate", "https://teacherrecord.com/tefl-certificate")
        st.link_button("Baamboozle Games", "https://www.baamboozle.com/")
        st.link_button("ABCya! Learning Fun", "https://www.abcya.com/")
        st.link_button("Oxford University Press", "
