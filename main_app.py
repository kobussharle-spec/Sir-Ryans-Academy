import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import pdfplumber

# --- 1. FOUNDATION & THEME ENGINE ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# Theme Selection in Sidebar
if "theme" not in st.session_state:
    st.session_state.theme = "Royal Navy"

# --- 2. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "nickname": "Scholar", 
        "avatar": None, "mute": False, "english_level": "Pending", 
        "current_subject": "General English",
        "progress": {"Grammar": 45, "Tenses": 30, "Vocab": 60, "Business": 20},
        "vault": {}, "feedback_log": ""
    })

# Apply Snassy CSS based on theme
if st.session_state.theme == "Royal Navy":
    primary, accent = "#002147", "#C5A059"
else:
    primary, accent = "#4B0082", "#FFD700" # Imperial Purple

st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {primary};
        color: {accent};
        border-radius: 20px;
        border: 2px solid {accent};
        font-weight: bold;
    }}
    .stMetric {{ background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid {primary}; }}
    </style>
    """, unsafe_allow_html=True)

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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.session_state.theme = st.radio("Academy Theme:", ["Royal Navy", "Imperial Purple"])
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, width=150)
    st.info(f"🏅 Level: {st.session_state.english_level}")
    
    subjects = ["General English", "Tenses", "Grammar Mastery", "Business English", "🏆 GRAND FINAL"]
    st.session_state.current_subject = st.selectbox("Focus Area:", subjects)
    
    st.divider()
    st.markdown("### 🏛️ Library Vault")
    with st.expander("📚 RESOURCES"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Grammar", "https://www.bbc.co.uk/learningenglish/english/grammar")
    
    st.divider()
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    name_in = st.text_input("Full Name:")
    key_in = st.text_input("License Key:", type="password")
    if st.button("Register & Enter Academy"):
        if key_in.lower().strip() == "oxford2026":
            st.session_state.authenticated = True
            st.session_state.nickname = name_in
            st.rerun()
    st.stop()

# --- 6. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")

# --- 7. THE STUDY DESKS (HOMEWORK & FEEDBACK) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Elocution")
    audio_data = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Submit", key='oral_v3')
    if audio_data:
        st.audio(audio_data['bytes'])

with col_right:
    st.subheader("📝 PDF Homework & Feedback")
    hw_file = st.file_uploader("Upload Workbook:", type=['pdf'])
    if hw_file and st.button("📤 Secure in Vault"):
        with pdfplumber.open(hw_file) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.vault[hw_file.name] = text
        st.success("Parchment secured!")

    if st.session_state.vault:
        sel_doc = st.selectbox("Select document:", list(st.session_state.vault.keys()))
        doc_q = st.text_input("Ask Sir Ryan about this file:")
        if st.button("🧐 Analyse"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Critique the homework."},{"role": "user", "content": f"Text: {st.session_state.vault[sel_doc][:5000]}\nQ: {doc_q}"}]).choices[0].message.content
            st.session_state.feedback_log += f"\n--- {sel_doc} ---\n{resp}\n"
            st.info(resp)
            speak_text(resp)
            
        # DOWNLOAD BUTTON
        if st.session_state.feedback_log:
            st.download_button(
                label="📥 Download Sir Ryan's Feedback",
                data=st.session_state.feedback_log,
                file_name="academy_feedback.txt",
                mime="text/plain"
            )

# ---
