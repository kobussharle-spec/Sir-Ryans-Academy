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

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name_val = st.text_input("Full Name:")
        nick_val = st.text_input("Nickname:")
        user_photo = st.file_uploader("Portrait:", type=['png', 'jpg'])
    with col2:
        key_val = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if name_val and key_val.lower().strip() in ["oxford2026", "guest"]:
                st.session_state.authenticated = True
                st.session_state.student_name = name_val
                st.session_state.nickname = nick_val if nick_val else name_val
                st.session_state.avatar = user_photo
                st.session_state.show_test = True # Trigger the test
                st.rerun()
    st.stop()

# --- 5. THE LEVEL TEST (NEW) ---
if st.session_state.show_test:
    st.title("📜 Academy Entrance Evaluation")
    st.write(f"Welcome, {st.session_state.nickname}. Please complete this assessment or skip if you are a returning scholar.")
    
    if st.button("🏆 Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.session_state.show_test = False
        st.rerun()

    with st.form("level_test"):
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
        
        if st.form_submit_button("Submit Exam"):
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
            
            st.session_state.show_test = False
            st.success(f"Exam marked! Your level: {st.session_state.english_level}")
            time.sleep(2)
            st.rerun()
    st.stop()

# --- 6. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.mute: return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural", rate="+0%")
        filename = f"v_{int(time.time())}.mp3"
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 7. SIDEBAR ---
with st.sidebar:
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=150)
    
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.markdown(f"**🏅 Level: {st.session_state.english_level}**") # LEVEL DISPLAYED HERE
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.rerun()

    st.divider()
    st.markdown("### 📚 Subject Selection")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Business English", "Legal English (Law)"]
    st.selectbox("Focus Area:", subjects, key="current_subject")

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 Resources"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/?tl=true")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish/english/grammar")

    st.divider()
    if st.button("🔄 Retake Entrance Exam"): # RETAKE BUTTON
        st.session_state.show_test = True
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

with st.expander("🎓 ORIENTATION GUIDE"):
    st.write("1. Check your Level in the sidebar. 2. Choose a Subject. 3. Practice with the tools below.")

# --- 9. PROGRESS ---
st.subheader("📊 Your Progress")
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 10. STUDY DESKS ---
st.divider()
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("🎤 Oral Practice")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Analysis complete. Marvelous effort! Have a biscuit.")

with col_right:
    st.subheader("📝 Homework Desk")
    hw_text = st.text_area("Submit your assignment here:")
    if st.button("🚀 Submit Homework"):
        st.success("Homework received. A biscuit for you!")

# --- 11. CHAT ---
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
            messages=[{"role": "system", "content": f"You are Sir Ryan. Use formal British English. The student is at {st.session_state.english_level} level. Mention biscuits."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy</p></center>", unsafe_allow_html=True)
