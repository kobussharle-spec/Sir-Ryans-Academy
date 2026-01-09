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
        "english_level": "Pending", "test_score": 0, "show_test": False,
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0},
        "access_level": "Guest"
    })

# --- 4. THE GATEKEEPER (The Only Way In) ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name_input = st.text_input("Full Name:")
        nick_input = st.text_input("Nickname:")
        user_photo = st.file_uploader("Portrait:", type=['png', 'jpg'])
    with col2:
        key_input = st.text_input("License Key:", type="password")
        if st.button("Register & Proceed to Entrance Exam"):
            if name_input and key_input.lower().strip() in ["oxford2026", "guest"]:
                st.session_state.authenticated = True
                st.session_state.student_name = name_input
                st.session_state.nickname = nick_input if nick_input else name_input
                st.session_state.avatar = user_photo
                st.session_state.english_level = "Pending" # Force the test trigger
                st.rerun()
    st.stop()

# --- 5. THE EXAMINATION ROOM (Fenced Off) ---
# If they are logged in but haven't done the test, they stay here!
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    st.title("📜 Academy Entrance Evaluation")
    st.markdown("### *You must complete this assessment to enter the Main Hall.*")
    
    if st.button("🏆 I am a Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()

    st.divider()
    with st.form("level_test"):
        st.subheader("Placement Exam")
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
            
            st.session_state.test_score = score
            if score <= 4: st.session_state.english_level = "Beginner"
            elif score <= 8: st.session_state.english_level = "Intermediate"
            else: st.session_state.english_level = "Advanced Executive"
            
            st.success(f"Exam marked! Level assigned: {st.session_state.english_level}")
            time.sleep(1)
            st.rerun()
    st.stop() # Stops them from seeing the main hall until form is submitted

# --- 6. THE MAIN ACADEMY (Only accessible after level is set) ---

# Voice Function
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

with st.sidebar:
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: **{st.session_state.english_level}**")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

    st.divider()
    st.markdown("### 📚 Subjects")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep"]
    st.selectbox("Focus:", subjects, key="current_subject")
    
    st.divider()
    st.markdown("### 🏛️ Library")
    with st.expander("Links"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("BBC Grammar", "https://www.bbc.co.uk/learningenglish/english/grammar")

    if st.button("🔄 Retake Level Test"):
        st.session_state.english_level = "Pending"
        st.rerun()

# --- HUB CONTENT ---
st.title(f"Welcome to the Main Hall, {st.session_state.nickname}!")
st.subheader(f"Academy Status: {st.session_state.english_level} Scholar")

with st.expander("📖 HOW TO USE THE ACADEMY"):
    st.write("1. Check your level. 2. Select a subject. 3. Complete homework. 4. Chat with Sir Ryan.")

# Progress
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("🎤 Oral Examination")
    mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Save")
with col2:
    st.subheader("📝 Homework Desk")
    st.text_area("Submit assignment:")
    st.button("🚀 Submit")

# Chat
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
            messages=[{"role": "system", "content": f"You are Sir Ryan. Speak to a {st.session_state.english_level} student. Mention biscuits."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session
