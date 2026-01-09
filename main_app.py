import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. THE GRAND ENTRANCE (LOGO restoration) ---
col_logo, _ = st.columns([1, 2])
with col_logo:
    try:
        st.image("logo.png", width=350)
    except:
        # If the file is missing, we show a majestic digital crest
        st.markdown("""
            <div style="background-color: #002147; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; text-align: center;">
                <h1 style="color: #C5A059; margin: 0; font-family: 'Times New Roman';">🏛️</h1>
                <h2 style="color: #C5A059; margin: 0; letter-spacing: 2px;">SIR RYAN'S ACADEMY</h2>
                <p style="color: #C5A059; font-style: italic;">English Excellence</p>
            </div>
        """, unsafe_allow_html=True)

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
        user_photo = st.file_uploader("Upload Portrait for Academy Records:", type=['png', 'jpg', 'jpeg'])
    with col2:
        key_input = st.text_input("License Key:", type="password")
        if st.button("Register & Proceed to Entrance Exam"):
            if name_input and key_input.lower().strip() in ["oxford2026", "guest"]:
                st.session_state.authenticated = True
                st.session_state.access_level = "Full" if key_input.lower().strip() == "oxford2026" else "Guest"
                st.session_state.student_name = name_input
                st.session_state.nickname = nick_input if nick_input else name_input
                st.session_state.avatar = user_photo
                st.rerun()
    st.stop()

# --- 5. THE EXAMINATION ROOM ---
if st.session_state.english_level == "Pending":
    st.title("📜 Academy Entrance Evaluation")
    st.markdown("### Welcome, Scholar. Please complete your placement exam.")
    
    if st.button("🏆 I am a Returning Scholar (Skip Test)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()

    st.divider()
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

# --- 7. SIDEBAR ---
with st.sidebar:
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

    st.divider()
    st.markdown("### 📚 Subject Selection")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep"]
    st.selectbox("Focus Area:", subjects, key="current_subject")

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 Study Resources"):
        st.link_button("Oxford English Dictionary", "https://www.oed.com/?tl=true")
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
    st.markdown("### 📞 Academy Support")
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🔄 Retake Level Test"):
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# Orientation Guide
with st.expander("🎓 NEW SCHOLAR ORIENTATION (Read First)"):
    st.markdown("""
    1. **Check Your Level**: Look at your sidebar to see your placement result.
    2. **Oral Practice**: Record your voice for elocution feedback.
    3. **Homework**: Submit your written tasks or upload reports below.
    4. **Translator**: Use the desk to convert your home language to Posh English.
    5. **Chat**: Ask Sir Ryan anything! He loves discussing biscuits.
    """)

# Progress
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. THE STUDY DESKS ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Analysis complete. Marvelous effort! Have a biscuit.")
    
    st.divider()
    st.subheader("📝 Translator Desk")
    source_lang = st.selectbox("From:", ["Afrikaans", "Spanish", "French", "German"])
    t_text = st.text_area("Type here:")
    if st.button("Translate to British English"):
        if t_text:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": f"Translate {source_lang} to formal British English."},
                          {"role": "user", "content": t_text}]
            ).choices[0].message.content
            st.info(res)

with col_right:
    st.subheader("📝 Homework Desk")
    hw_text = st.text_area("1. Write your assignment here:", height=150)
    if st.button("🚀 Submit Written Homework"):
        st.success("Written homework received! You've earned a biscuit.")
    
    st.divider()
    hw_file = st.file_uploader("2. Or upload a file (PDF/DOCX):", type=['pdf', 'docx', 'txt'])
    if st.button("📤 Upload Homework File"):
        if hw_file: st.success(f"File '{hw_file.name}' received.")

# --- 10. CHAT HUB (THE AUDIENCE WITH SIR RYAN) ---
st.divider()
st.subheader("💬 Audience with the Headmaster")

# Display the conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# The Chat Input Box
if prompt := st.chat_input("Ask Sir Ryan a question about English or etiquette..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Sir Ryan's response
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are Sir Ryan, the formal and posh British Headmaster of the Academy. You are speaking to a {st.session_state.english_level} student. Be encouraging but very professional. Swapping cookies for biscuits. Mention biscuits occasionally. Use extra 'u's in words like colour and honour."}
                ] + st.session_state.messages
            ).choices[0].message.content
            
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            
            # Voice output
            speak_text(resp)
        except Exception as e:
            st.error("The Headmaster is currently at tea. Please try again in a moment.")

# --- 11. THE ACADEMY FOOTER & COPYRIGHT ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
    <center>
        <p style='color: #888888; font-size: 0.9em;'>
            © 2026 J Steenekamp | 🏛️ Sir Ryan's Academy of English Excellence | All Rights Reserved
        </p>
    </center>
""", unsafe_allow_html=True)
