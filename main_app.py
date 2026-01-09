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

# >>> INSERT THE LOGO SECTION RIGHT HERE! <<<

# --- 2. THEMES & STYLING ---

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
        "english_level": "Beginner", "theme": "Oxford Blue"
    })

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name:")
        nick = st.text_input("Nickname (for Sir Ryan to use):")
        photo = st.file_uploader("Upload your portrait (optional):", type=['png', 'jpg'])
    with col2:
        key = st.text_input("License Key:", type="password")
        lang = st.selectbox("Your Home Language (for translator):", ["None", "Afrikaans", "Spanish", "French", "German", "Mandarin"])
    
    if st.button("Register & Enter Academy"):
        if name and key.lower().strip() in ["oxford2026", "guest"]:
            st.session_state.authenticated = True
            st.session_state.student_name = name
            st.session_state.nickname = nick if nick else name
            if photo: st.session_state.avatar = photo
            st.rerun()
    st.stop()

# --- 5. SIR RYAN'S VOICE ENGINE ---
def speak_text(text):
    if st.session_state.mute: return
    try:
        # Sir Ryan is now formal - no "Chap" or "Mate"
        clean = text.replace("**", "").replace("#", "")
        # Standard speed for clarity as requested by daughter
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural", rate="+0%")
        filename = f"v_{int(time.time())}.mp3"
        asyncio.run(communicate.save(filename))
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 6. THE SIDEBAR (REBUILT) ---
with st.sidebar:
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=100)
    st.markdown(f"### Welcome, {st.session_state.nickname}")
    
    # Mute Button
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan", value=st.session_state.mute)
    
    st.divider()
    st.markdown("### 📚 Subject Selection")
    subjects = [
        "General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", 
        "Writing: Emails", "Writing: Letters", "Writing: Reports", "Business English",
        "Medical English", "Legal English (Law)", "Maths in English", "Arts & Culture",
        "Preparation for ELS", "Interview Excellence", "British Idioms"
    ]
    st.selectbox("Focus Area:", subjects, key="current_subject")

    st.divider()
    st.markdown("### ⚙️ Settings & Theme")
    st.session_state.theme = st.radio("Choose Academy Theme:", list(theme_styles.keys()))
    
    st.divider()
    st.markdown("### 🏛️ Library & Resources")
    st.link_button("Oxford Dictionary", "https://www.oed.com/")
    st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
    st.link_button("WhatsApp Dean", "https://wa.me/27833976517")

# --- 7. INTRO STEP GUIDE (USER MANUAL) ---
with st.expander("📖 NEW SCHOLAR: HOW TO USE THE ACADEMY (Intro Guide)"):
    st.write("""
    1. **Sidebar**: Choose your subject and theme here. This is your 'backpack'.
    2. **Oral Exam**: Record yourself speaking. Sir Ryan will listen and help you.
    3. **Chat Hub**: Type questions below. Sir Ryan will answer in a posh British accent.
    4. **Mute**: Use the checkbox in the sidebar if you wish Sir Ryan to remain silent.
    """)

# --- 8. PROGRESS PAGE (Personal Page) ---
st.divider()
st.subheader(f"📊 {st.session_state.nickname}'s Progress")
cols = st.columns(len(st.session_state.progress))
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. MAIN INTERFACE ---
st.divider()
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("🎤 Oral Practice")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Sir Ryan is analyzing your elocution...")

with col_right:
    st.subheader("📝 Translator (Helper)")
    st.text_area("Struggling? Type in your language here to see the English version:")
    st.button("Translate to English")

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
            messages=[{"role": "system", "content": "You are Sir Ryan, a very formal British Headmaster. No 'mate' or 'chap'. Talk clearly and mention biscuits."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
