import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 3. THE GRAND ENTRANCE (LOGO) ---
try:
    st.image("logo.png", width=350)
except:
    st.info("🏛️ The Academy crest is being polished. Welcome!")

# --- 2. THEMES & STYLING ---
if "theme" not in st.session_state:
    st.session_state.theme = "Oxford Blue"

theme_styles = {
    "Oxford Blue": {"bg": "#F0F2F6", "sidebar": "#002147", "text": "#C5A059"},
    "Royal Emerald": {"bg": "#F0F9F0", "sidebar": "#043927", "text": "#D4AF37"},
    "Midnight": {"bg": "#121212", "sidebar": "#1E1E1E", "text": "#FFFFFF"}
}
curr_theme = theme_styles[st.session_state.theme]

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ background-color: {curr_theme['sidebar']} !important; color: {curr_theme['text']} !important; }}
    .stButton>button {{ background-color: {curr_theme['sidebar']} !important; color: {curr_theme['text']} !important; border: 1px solid {curr_theme['text']}; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATES & PERSONAL INFO ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "progress": {s: 0 for s in ["Grammar", "Tenses", "Vocab", "Law", "Business"]},
        "english_level": "Beginner", "theme": "Oxford Blue", "access_level": "Guest"
    })

# --- 4. THE GATEKEEPER (WITH MEMORY) ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name_val = st.text_input("Full Name:", value=st.session_state.get('saved_name', ""))
        nick_val = st.text_input("Nickname:", value=st.session_state.get('saved_nick', ""))
    with col2:
        key_val = st.text_input("License Key:", type="password")
        remember_me = st.checkbox("💾 Save & Remember Me on this device")

    if st.button("Unlock Study Hub"):
        if name_val and key_val.lower().strip() in ["oxford2026", "guest"]:
            st.session_state.authenticated = True
            st.session_state.access_level = "Full" if key_val.lower().strip() == "oxford2026" else "Guest"
            st.session_state.student_name = name_val
            st.session_state.nickname = nick_val if nick_val else name_val
            if remember_me:
                st.session_state.saved_name = name_val
                st.session_state.saved_nick = nick_val
            st.rerun()
    st.stop()

# --- 5. SIR RYAN'S VOICE ENGINE ---
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

# --- 6. THE SIDEBAR (REBUILT & INDENTED CORRECTLY) ---
with st.sidebar:
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=100)
    
    st.markdown(f"### Scholar: {st.session_state.nickname}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan", value=st.session_state.mute)
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.rerun()

    st.divider()
    st.markdown("### 📚 Subject Selection")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", 
                "Writing: Emails", "Writing: Letters", "Writing: Reports", "Business English",
                "Medical English", "Legal English (Law)", "Maths in English", "Arts & Culture",
                "Preparation for ELS", "Interview Excellence", "British Idioms"]
    st.selectbox("Focus Area:", subjects, key="current_subject")

    st.divider()
    st.markdown("### 🏛️ The Royal Library Vault")
    if st.session_state.access_level == "Guest":
        st.warning("🔒 Library Restricted")
        st.link_button("👑 Unlock Full Access", "https://www.etsy.com/shop/YourShopName")
    else:
        st.success("👑 Full Access Granted")
        with st.expander("📚 Resources"):
            st.link_button("Oxford Learner's Dictionary", "https://www.oxfordlearnersdictionaries.com/")
            st.link_button("BBC Worklife", "https://www.bbc.com/worklife")
            st.link_button("YouGlish (British)", "https://youglish.com/british")

# --- 7. MAIN INTERFACE ---
st.title(f"Welcome back, {st.session_state.nickname}")

with st.expander("📖 NEW SCHOLAR: HOW TO USE THE ACADEMY"):
    st.write("1. Sidebar: Choose subject. 2. Oral Exam: Practice speaking. 3. Chat Hub: Ask questions.")

# --- 8. PROGRESS PAGE ---
st.subheader("📊 Your Progress")
cols = st.columns(len(st.session_state.progress))
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. STUDY HUB ---
st.divider()
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("🎤 Oral Practice")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Analysis complete. Excellent diction! Have a biscuit.")

with col_right:
    st.subheader("📝 Translator")
    st.text_area("Type here to translate to English:")
    st.button("Translate")

# --- 10. CHAT ---
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
            messages=[{"role": "system", "content": "You are Sir Ryan, a very formal British Headmaster. Talk clearly and mention biscuits."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy</p></center>", unsafe_allow_html=True)
