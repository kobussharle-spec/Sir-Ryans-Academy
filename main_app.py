import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber
import io

# --- 1. FOUNDATION & SNASSY STYLING ---
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
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #C5A059; color: #002147; border: 2px solid #002147; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "current_subject": "General English",
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0},
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
        if st.button("Register & Begin Placement Exam"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.session_state.avatar = u_photo
                st.rerun()
    st.stop()

# --- 5. LEVEL ASSESSMENT (AFTER LOGIN) ---
if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Evaluation")
    st.markdown("### Welcome, Scholar. Please complete these 10 questions to determine your rank.")
    with st.form("level_test"):
        q1 = st.radio("1. TENSES: By this time tomorrow, I _______ my assignment.", ["will finish", "will have finished", "finished"])
        q2 = st.radio("2. GRAMMAR: Which sentence is correct?", ["Who's bag is this?", "Whose bag is this?", "Whom bag is this?"])
        q3 = st.radio("3. GENERAL: A 'biscuit' in London is a _______ in New York.", ["cookie", "cracker", "muffin"])
        q4 = st.radio("4. TENSES: I _______ English for three years now.", ["study", "am studying", "have been studying"])
        q5 = st.radio("5. GRAMMAR: If I _______ you, I would take the job.", ["was", "were", "am"])
        q6 = st.radio("6. GENERAL: Which is a formal greeting?", ["How's it going?", "Good morning, Sir.", "Hey there!"])
        q7 = st.radio("7. TENSES: She _______ to the theatre yesterday.", ["has gone", "went", "goes"])
        q8 = st.radio("8. GRAMMAR: Choose the correctly spelled word:", ["Honour", "Honor", "Honur"])
        q9 = st.radio("9. GENERAL: 'To be chuffed' means you are:", ["Angry", "Pleased", "Tired"])
        q10 = st.radio("10. TENSES: Listen! The birds _______.", ["sing", "are singing", "sang"])
        
        if st.form_submit_button("Submit Evaluation"):
            score = 0
            if q1 == "will have finished": score += 1
            if q2 == "Whose bag is this?": score += 1
            if q3 == "cookie": score += 1
            if q4 == "have been studying": score += 1
            if q5 == "were": score += 1
            if q6 == "Good morning, Sir.": score += 1
            if q7 == "went": score += 1
            if q8 == "Honour": score += 1
            if q9 == "Pleased": score += 1
            if q10 == "are singing": score += 1
            
            if score <= 4: st.session_state.english_level = "Beginner (Lower School)"
            elif score <= 8: st.session_state.english_level = "Intermediate (Middle School)"
            else: st.session_state.english_level = "Advanced (Senior Scholar)"
            st.success(f"Assessment complete! Your Rank: {st.session_state.english_level}")
            time.sleep(2)
            st.rerun()
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Rank: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 RESOURCES"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Grammar Guide", "https://www.bbc.co.uk/learningenglish/english/grammar")

    st.divider()
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 7. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")

# --- 8. THE STUDY DESKS ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Elocution")
    audio_data = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ End & Submit", key='oral_rec')
    if audio_data:
        st.audio(audio_data['bytes'])
        if st.button("👂 Ask Sir Ryan to Critique"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
            with open("temp.wav", "rb") as af:
                trans = client.audio.transcriptions.create(file=("temp.wav", af.read()), model="whisper-large-v3", response_format="text")
            st.markdown(f"**Sir Ryan heard:** *\"{trans}\"*")
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Critique elocution. Mention biscuits."},{"role": "user", "content": trans}]).choices[0].message.content
            st.info(resp); speak_text(resp)

with col_right:
    st.subheader("📝 PDF Vault & Research")
    hw_file = st.file_uploader("Upload Workbook (PDF):", type=['pdf'])
    if hw_file and st.button("📤 Secure in Vault"):
        with pdfplumber.open(hw_file) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.vault[hw_file.name] = text
        st.success("Document archived!")

    if st.session_state.vault:
        sel_doc = st.selectbox("Select document:", list(st.session_state.vault.keys()))
        doc_q = st.text_input("Ask Sir Ryan about this file:")
        if st.button("🧐 Analyse"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "Answer based on PDF."},{"role": "user", "content": f"Text: {st.session_state.vault[sel_doc][:5000]}\nQ: {doc_q}"}]).choices[0].message.content
            st.info(resp); speak_text(resp)

# --- 9. CHAT HUB ---
st.divider()
st.subheader("💬 Audience with the Headmaster")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])
if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Mention biscuits and use extra 'u's."}] + st.session_state.messages).choices[0].message.content
        st.markdown(resp); st.session_state.messages.append({"role": "assistant", "content": resp}); speak_text(resp)

st.markdown("<br><hr><center><p>© 2026 J Steenekamp | Sir Ryan's Academy</p></center>", unsafe_allow_html=True)
