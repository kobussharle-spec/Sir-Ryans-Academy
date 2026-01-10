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
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #C5A059; color: #002147; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #C5A059; margin-bottom: 20px; }
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
if "avatar" not in st.session_state:
    st.session_state.avatar = None
if "progress" not in st.session_state:
    st.session_state.progress = {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0}

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
            <div style="background-color: #002147; padding: 15px; border-radius: 10px; border: 2px solid #C5A059; text-align: center; width: {width}px;">
                <h2 style="color: #C5A059; margin: 0; font-family: 'Times New Roman';">🏛️ SIR RYAN'S ACADEMY</h2>
                <p style="color: #C5A059; font-size: 0.8em; margin: 0;">Excellence & Honour</p>
            </div>
        """, unsafe_allow_html=True)

# --- 5. THE LOGIN GATE (PORTRAIT UPLOAD INCLUDED) ---
if not st.session_state.authenticated:
    display_academy_logo()
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:", key="reg_name")
        nick_in = st.text_input("Nickname:", key="reg_nick")
        u_photo = st.file_uploader("Upload Portrait for Academy Records:", type=['png', 'jpg', 'jpeg'], key="reg_photo")
    with c2:
        key_in = st.text_input("License Key:", type="password", key="reg_key")
        if st.button("Register & Begin Placement Exam"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.session_state.avatar = u_photo
                st.rerun()
            else:
                st.warning("Please ensure the name is filled and the key is 'oxford2026'.")
    st.stop()

# --- 6. ENTRANCE EVALUATION ---
if st.session_state.authenticated and st.session_state.english_level == "Pending":
    display_academy_logo(width=200)
    st.title("📜 Entrance Evaluation")
    st.markdown(f"Welcome, {st.session_state.nickname}. Let us determine your rank.")
    with st.form("level_test"):
        e1 = st.radio("1. Which is the correct British spelling?", ["Color", "Colour"])
        e2 = st.radio("2. A 'biscuit' in London is a _______ in New York.", ["Cookie", "Muffin"])
        e3 = st.radio("3. I _______ (see) that film already.", ["saw", "have seen"])
        if st.form_submit_button("Submit Assessment"):
            st.session_state.english_level = "Scholar"
            st.success("Splendid! Welcome to the Academy.")
            time.sleep(1)
            st.rerun()
    st.stop()

# --- 7. SIDEBAR (LIBRARY & LINKS) ---
with st.sidebar:
    display_academy_logo(width=200)
    st.divider()
    if st.session_state.avatar:
        st.image(st.session_state.avatar, caption="Academy Portrait", use_container_width=True)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Rank: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Vocabulary", "Business English", "🏆 GRAND FINAL"]
    st.session_state.current_subject = st.selectbox("Current Module:", subjects)

    st.divider()
    st.markdown("### 📖 Library Vault")
    with st.expander("Essential Links"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/")
        st.link_button("Baamboozle Games", "https://www.baamboozle.com/")

    if st.button("🚪 Log Out"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 8. MAIN HUB ---
display_academy_logo(width=250)
st.title(f"Academy Hub: {st.session_state.current_subject}")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")

# --- 9. THE QUIZ ENGINE (TENSES MODULE) ---
st.divider()
st.subheader("✍️ Module Examination")
if st.session_state.current_subject == "Tenses":
    with st.form("tenses_quiz"):
        st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
        q1 = st.radio("1. By the time he arrived, we _______ (finish) dinner.", ["finished", "had finished", "have finished"])
        q2 = st.radio("2. I _______ (live) in London for five years now.", ["live", "am living", "have been living"])
        q3 = st.radio("3. Tomorrow at 10 AM, I _______ (sit) in my exam.", ["sit", "will be sitting", "will have sat"])
        # (Space for more questions as requested)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.form_submit_button("Submit for Marking"):
            st.success("Exam submitted! Sir Ryan is marking your papers. Have a biscuit!")
            st.session_state.progress["Tenses"] = 25
else:
    st.info(f"The curriculum for {st.session_state.current_subject} is currently being prepared.")

# --- 10. STUDY DESKS (ORAL & PDF) ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎤 Oral Elocution")
    audio = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ Submit", key='oral_v14')
    if audio:
        st.audio(audio['bytes'])
        if st.button("👂 Critique My Pronunciation"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with open("temp.wav", "wb") as f: f.write(audio['bytes'])
            with open("temp.wav", "rb") as af:
                trans = client.audio.transcriptions.create(file=("temp.wav", af.read()), model="whisper-large-v3", response_format="text")
            st.markdown(f"**Heard:** *\"{trans}\"*")
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Critique pronunciation. Use British spelling."},{"role": "user", "content": trans}]).choices[0].message.content
            st.info(resp); speak_text(resp)

with c2:
    st.subheader("📝 PDF & Homework Vault")
    hw = st.file_uploader("Upload Workbook (PDF):", type=['pdf'])
    if hw and st.button("📤 Archive to Vault"):
        with pdfplumber.open(hw) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.vault[hw.name] = text
        st.success(f"'{hw.name}' archived!")

    if st.session_state.vault:
        sel_doc = st.selectbox("Select File:", list(st.session_state.vault.keys()))
        doc_q = st.text_input("Ask Sir Ryan about this file:")
        if st.button("🧐 Analyse File"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "Answer based on text."},{"role": "user", "content": f"Text: {st.session_state.vault[sel_doc][:5000]}\nQ: {doc_q}"}]).choices[0].message.content
            st.info(resp); speak_text(resp)

# --- 11. WRITTEN ASSIGNMENT AREA ---
st.divider()
st.subheader("✒️ Written Assignment Desk")
assignment = st.text_area("Draft your essay or report here:", height=150)
if st.button("🚀 Submit Written Homework"):
    st.success("Submitted! A gold star and a biscuit for you!")

# --- 12. CHAT HUB ---
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
