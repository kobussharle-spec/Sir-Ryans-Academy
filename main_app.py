import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber
import io

# --- 1. THE FOUNDATION & SNASSY STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# This CSS creates the "Snassy" Navy and Gold look
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 20px;
        border: 2px solid #C5A059;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #C5A059;
        color: #002147;
        border: 2px solid #002147;
    }
    .stMetric { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #002147; 
    }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .stExpander { border: 1px solid #C5A059; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

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

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    col_logo, _ = st.columns([1, 2])
    with col_logo:
        st.markdown("""<div style="background-color: #002147; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; text-align: center;"><h1 style="color: #C5A059; margin: 0;">🏛️</h1><h2 style="color: #C5A059; margin: 0;">SIR RYAN'S ACADEMY</h2></div>""", unsafe_allow_html=True)
    
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

# --- 5. SIDEBAR (SUBJECTS & LINKS) ---
with st.sidebar:
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 RESOURCES"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/")
        st.link_button("BBC Grammar", "https://www.bbc.co.uk/learningenglish/english/grammar")

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN HUB (PROGRESS) ---
st.title(f"Good day, {st.session_state.nickname}!")
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 7. MASTERY QUIZZES (20 Questions / 100 Questions) ---
st.divider()
st.subheader(f"📝 {st.session_state.current_subject} Assessment")
with st.expander(f"Open {st.session_state.current_subject} Exam Paper"):
    num_qs = 100 if "GRAND FINAL" in st.session_state.current_subject else 20
    with st.form("quiz_form"):
        st.write(f"This paper contains {num_qs} questions. Accuracy is a matter of honour.")
        for i in range(1, num_qs + 1):
            st.radio(f"Question {i}: Select the correct British usage.", ["Option A", "Option B", "Option C"], key=f"q_{i}")
        if st.form_submit_button("Submit Exam Paper"):
            st.balloons()
            st.success("Splendid! Your results are being reviewed. Have a biscuit!")

# --- 8. THE STUDY DESKS (HOMEWORK & PDF VAULT) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Elocution (Sir Ryan Listens)")
    audio_data = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ End & Submit", key='oral_rec')
    if audio_data:
        st.audio(audio_data['bytes'])
        if st.button("👂 Ask Sir Ryan to Critique"):
            with st.spinner("Sir Ryan is adjusting his spectacles..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
                    with open("temp.wav", "rb") as af:
                        trans = client.audio.transcriptions.create(file=("temp.wav", af.read()), model="whisper-large-v3", response_format="text")
                    st.markdown(f"**Sir Ryan heard:** *\"{trans}\"*")
                    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Critique the student's speech for elocution. Mention biscuits and use British spelling."},{"role": "user", "content": trans}]).choices[0].message.content
                    st.info(resp)
                    speak_text(resp)
                except Exception as e: st.error(f"Error: {e}")

with col_right:
    st.subheader("📝 PDF Vault & Research Desk")
    hw_file = st.file_uploader("Upload Workbook or Report (PDF):", type=['pdf'])
    if hw_file and st.button("📤 Secure PDF in Vault"):
        try:
            with pdfplumber.open(hw_file) as pdf:
                text = "".join([page.extract_text() for page in pdf.pages])
            st.session_state.vault[hw_file.name] = text
            st.success(f"'{hw_file.name}' is now in the Academy Library!")
        except: st.error("Sir Ryan could not read that parchment.")

    if st.session_state.vault:
        sel_doc = st.selectbox("Select document to discuss:", list(st.session_state.vault.keys()))
        doc_q = st.text_input("Question for Sir Ryan about this PDF:")
        if st.button("🧐 Analyse Document"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Answer based on the provided text. Use British spelling."},{"role": "user", "content": f"Text: {st.session_state.vault[sel_doc][:5000]}\nQ: {doc_q}"}]).choices[0].message.content
            st.info(resp)
            speak_text(resp)

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
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Use British spelling and mention biscuits."}] + st.session_state.messages).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
