import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. LOGO ---
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

# --- 4. GATEKEEPER ---
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

# --- 5. LEVEL TEST (RESTORED) ---
if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🏆 Returning Scholar (Skip)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    with st.form("initial_test"):
        st.write("Determine your rank with these 10 questions...")
        # Placeholder for your 10 initial questions
        if st.form_submit_button("Submit Exam"):
            st.session_state.english_level = "Intermediate"
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
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Current Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 Resources"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/dictionary/english/explanatory")
        st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
        st.link_button("BBC Grammar Guide", "https://www.bbc.co.uk/learningenglish/english/grammar")
        st.link_button("English Level Test", "https://engxam.com/english-level-test/")
        st.link_button("TEFL Certificate", "https://teacherrecord.com/tefl-certificate")
        st.link_button("Baamboozle Games", "https://www.baamboozle.com/")
        st.link_button("ABCya! Learning Fun", "https://www.abcya.com/")
        st.link_button("Oxford University Press", "https://elt.oup.com/learning_resources/")
        st.link_button("Cambridge Support", "https://www.cambridgeenglish.org/supporting-learners/?level=basic")

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. THE MASTERY WING (QUIZZES) ---
st.divider()
st.subheader(f"📝 {st.session_state.current_subject} Mastery Quiz")

# This section handles both 20-question subject quizzes and the 100-question final
with st.expander(f"Click to start the {st.session_state.current_subject} Examination"):
    num_questions = 100 if "GRAND FINAL" in st.session_state.current_subject else 20
    with st.form("subject_quiz"):
        st.write(f"This assessment contains {num_questions} questions on {st.session_state.current_subject}.")
        # To keep the code clean, we use a loop for placeholders
        for i in range(1, num_questions + 1):
            st.radio(f"Question {i}: Select the most formal option.", ["Option A", "Option B", "Option C"], key=f"q{i}")
        
        if st.form_submit_button("Submit Examination"):
            st.balloons()
            st.success(f"Splendid! Your results for {st.session_state.current_subject} have been recorded. Have a biscuit!")

# --- 10. THE STUDY DESKS (RESTORED BEST LAYOUT) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Analysis complete. Marvelous effort!")

with col_right:
    st.subheader("📝 Homework Desk")
    hw_text = st.text_area("1. Write your assignment here:")
    if st.button("🚀 Submit Written Homework"):
        st.success("Written homework received! A biscuit for you.")
    st.divider()
    hw_file = st.file_uploader("2. Or upload a file:", type=['pdf', 'docx', 'txt'])
    if st.button("📤 Upload Homework File"):
        if hw_file: st.success(f"File '{hw_file.name}' received.")

# --- 11. CHAT HUB & COPYRIGHT (RESTORED) ---
st.divider()
st.subheader("💬 Audience with the Headmaster")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "
