import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber  # FLUSH LEFT AT THE TOP

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. SESSION STATES (The Academy Records) ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, 
        "messages": [], 
        "student_name": "Scholar",
        "nickname": "Scholar", 
        "avatar": None, 
        "mute": False,
        "english_level": "Pending", 
        "current_subject": "General English",
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0},
        "vault": {}  # Personal Library for PDFs
    })

# --- 3. LOGO / CREST ---
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

# --- 4. VOICE ENGINE ---
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

# --- 5. THE GATEKEEPER ---
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

# --- 6. LEVEL TEST ---
if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🏆 Returning Scholar (Skip)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    with st.form("initial_test"):
        st.write("Determine your rank with 10 initial questions...")
        # Add your specific level test questions here
        if st.form_submit_button("Submit Exam"):
            st.session_state.english_level = "Intermediate"
            st.rerun()
    st.stop()

# --- 7. SIDEBAR (The Control Room) ---
with st.sidebar:
    if st.session_state.avatar: 
        st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    if st.button("🔄 Retake Level Test"):
        st.session_state.english_level = "Pending"
        st.rerun()
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Business English", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Current Focus Area:", subjects)

    st.divider()
    st.markdown("### 🏛️ Scholar's Personal Vault")
    if st.session_state.vault:
        for filename in st.session_state.vault.keys():
            st.caption(f"📄 {filename}")
    else:
        st.caption("Vault is empty.")

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. MASTERY QUIZZES ---
st.divider()
st.subheader(f"📝 {st.session_state.current_subject} Mastery Quiz")
with st.expander(f"Open {st.session_state.current_subject} Quiz"):
    num_qs = 100 if "GRAND FINAL" in st.session_state.current_subject else 20
    with st.form("quiz_form"):
        for i in range(1, num_qs + 1):
            st.radio(f"Question {i}: Select the correct form.", ["Option A", "Option B", "Option C"], key=f"q{i}")
        if st.form_submit_button("Submit Examination"):
            st.balloons()
            st.success("Splendid effort! Results archived.")

# --- 10. STUDY DESKS (Oral & PDF Vault) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Elocution")
    audio_data = mic_recorder(start_prompt="⏺️ Begin Speaking", stop_prompt="⏹️ End & Submit", key='oral_rec')
    if audio_data:
        st.audio(audio_data['bytes'])
        if st.button("👂 Sir Ryan, did you hear that?"):
            with st.spinner("Headmaster is listening..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
                    with open("temp.wav", "rb") as af:
                        transcription = client.audio.transcriptions.create(file=("temp.wav", af.read()), model="whisper-large-v3", response_format="text")
                    st.markdown(f"**Heard:** *\"{transcription}\"*")
                    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Critique the student's speech. Mention biscuits."},{"role": "user", "content": transcription}]).choices[0].message.content
                    st.info(resp)
                    speak_text(resp)
                except: st.error("Ear trumpet failure!")

with col_right:
    st.subheader("📝 PDF Research Desk")
    hw_file = st.file_uploader("Upload Workbook to Vault:", type=['pdf'])
    if hw_file and st.button("📤 Process & Save"):
        with pdfplumber.open(hw_file) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.vault[hw_file.name] = text
        st.success("Stored in Vault!")

    if st.session_state.vault:
        sel_doc = st.selectbox("Select document to discuss:", list(st.session_state.vault.keys()))
        doc_q = st.text_input("Ask Sir Ryan about this document:")
        if st.button("🧐 Analyse"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Review the document context and answer the question."},{"role": "user", "content": f"Context: {st.session_state.vault[sel_doc][:5000]}\nQuestion: {doc_q}"}]).choices[0].message.content
            st.info(resp)
            speak_text(resp)

# --- 11. CHAT HUB & FOOTER ---
st.divider()
st.subheader("💬 Audience with the Headmaster")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])
if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are Sir Ryan. Level: {st.session_state.english_level}. Use British spelling and mention biscuits."}] + st.session_state.messages).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
