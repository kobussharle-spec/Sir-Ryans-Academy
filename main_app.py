import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "current_subject": "General English",
        "progress": {"Grammar": 45, "Tenses": 30, "Vocab": 60, "Business": 20},
        "vault": {}
    })

# --- 3. VOICE ENGINE ---
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

# --- 4. GATEKEEPER & LEVEL TEST ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:")
        nick_in = st.text_input("Nickname:")
        u_photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        key_in = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.session_state.avatar = u_photo
                st.rerun()
    st.stop()

if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🏆 Skip to Advanced Executive"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    with st.form("entry_exam"):
        st.write("10 Questions to determine your rank...")
        if st.form_submit_button("Submit Exam"):
            st.session_state.english_level = "Intermediate"
            st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    if st.button("🔄 Retake Level Test"):
        st.session_state.english_level = "Pending"
        st.rerun()
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Current Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 RESOURCES"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/dictionary/english/explanatory")
        st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
        st.link_button("BBC Grammar Guide", "https://www.bbc.co.uk/learningenglish/english/grammar")
        st.link_button("English Level Test", "https://engxam.com/english-level-test/")
        st.link_button("TEFL Certificate", "https://teacherrecord.com/tefl-certificate")
        st.link_button("Baamboozle Games", "https://www.baamboozle.com/")
        st.link_button("ABCya!", "https://www.abcya.com/")
        st.link_button("Oxford Press", "https://elt.oup.com/learning_resources/")
        st.link_button("Cambridge Support", "https://www.cambridgeenglish.org/supporting-learners/?level=basic")

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN HUB (PROGRESS RESTORED) ---
st.title(f"Good day, {st.session_state.nickname}!")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 7. MASTERY QUIZZES ---
st.divider()
st.subheader(f"📝 {st.session_state.current_subject} Mastery Quiz")
with st.expander(f"Take the {st.session_state.current_subject} Assessment"):
    num_qs = 100 if "GRAND FINAL" in st.session_state.current_subject else 20
    with st.form("mastery_quiz"):
        st.write(f"This assessment contains {num_qs} questions.")
        for i in range(1, num_qs + 1):
            st.radio(f"Question {i}: Identify the correct usage.", ["Choice A", "Choice B", "Choice C"], key=f"quiz_{i}")
        if st.form_submit_button("Submit Answers"):
            st.balloons()
            st.success("Splendid! Results archived. Have a biscuit!")

# --- 8. THE STUDY DESKS (HOMEWORK RESTORED) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Elocution")
    audio_data = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ End & Submit", key
