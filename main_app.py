import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. LOGO/CREST ---
col_logo, _ = st.columns([1, 2])
with col_logo:
    try:
        st.image("logo.png", width=350)
    except:
        st.markdown("""
            <div style="background-color: #002147; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; text-align: center;">
                <h1 style="color: #C5A059; margin: 0;">🏛️</h1>
                <h2 style="color: #C5A059; margin: 0; letter-spacing: 2px;">SIR RYAN'S ACADEMY</h2>
                <p style="color: #C5A059; font-style: italic;">Snassy English Excellence</p>
            </div>
        """, unsafe_allow_html=True)

# --- 3. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "current_subject": "General English",
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0}
    })

# --- 4. THE QUIZ DATA (THE LIBRARY) ---
# Dean, you can add all 20 questions for each subject here!
QUIZ_BANK = {
    "Tenses": [
        {"q": "I ____ (finish) my tea before he arrived.", "o": ["finished", "had finished", "was finish"], "a": "had finished"},
        # ... Add 19 more here
    ],
    "Business English": [
        {"q": "Which is more formal?", "o": ["Give a hand", "Assist", "Help out"], "a": "Assist"},
        # ... Add 19 more here
    ],
    "General English": [
        {"q": "A 'biscuit' in the UK is a ____ in the USA.", "o": ["Cookie", "Cracker", "Scone"], "a": "Cookie"},
        # ... Add 19 more here
    ]
}

# --- 5. THE GATEKEEPER & INITIAL LEVEL TEST ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name:")
        nick = st.text_input("Nickname:")
        photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg'])
    with c2:
        key = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if name and key.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name
                st.session_state.nickname = nick if nick else name
                st.session_state.avatar = photo
                st.rerun()
    st.stop()

# --- 6. LEVEL TEST (FORCE START) ---
if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🏆 Skip (Returning Scholar)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    
    with st.form("entry_exam"):
        st.write("10 Questions to determine your rank...")
        # (Insert your 10 questions here from previous code)
        if st.form_submit_button("Submit"):
            st.session_state.english_level = "Intermediate" # Logic here
            st.rerun()
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Business English", "Legal English", "Final 100 Exam"]
    st.session_state.current_subject = st.selectbox("Current Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 Links"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("WhatsApp Dean", "https://wa.me/27833976517")

    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 8. THE MAIN HUB ---
st.title(f"Welcome to the Hub, {st.session_state.nickname}!")

# --- 9. THE NEW QUIZ SECTION ---
st.divider()
st.subheader(f"📖 {st.session_state.current_subject}: Mastery Quiz")

if st.session_state.current_subject == "Final 100 Exam":
    st.warning("⚠️ Warning: This is the 100-Question Grand Final. Ensure you have a cup of tea ready.")
    if st.button("🏅 Start Grand Final"):
        st.info("Grand Final logic initialising...")
else:
    # Subject Specific Quiz (20 Questions)
    current_q_set = QUIZ_BANK.get(st.session_state.current_subject, [{"q": "Questions being added by the Dean...", "o": ["A", "B"], "a": "A"}])
    
    with st.form(f"quiz_{st.session_state.current_subject}"):
        st.write(f"Please complete these 20 questions on {st.session_state.current_subject}:")
        # Logic to loop through 20 questions
        for i, item in enumerate(current_q_set[:20]):
            st.radio(f"{i+1}. {item['q']}", item['o'], key=f"q_{i}")
        
        if st.form_submit_button("Submit Subject Quiz"):
            st.success("Marvelous! Your results have been recorded. Have a biscuit.")

# --- 10. STUDY TOOLS (Oral, Homework, Chat) ---
st.divider()
c_l, c_r = st.columns(2)
with c_l:
    st.subheader("🎤 Oral Practice")
    mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Save")

with c_r:
    st.subheader("📝 Homework Desk")
    st.text_area("Submit your essay:")
    st.file_uploader("Upload report:", type=['pdf', 'docx'])
    st.button("🚀 Submit Work")

# --- 11. CHAT & COPYRIGHT ---
st.divider()
st.subheader("💬 Chat with Sir Ryan")
# (Insert Chat Logic here)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | All Rights Reserved</p></center>", unsafe_allow_html=True)
