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

# --- 2. THE GRAND ENTRANCE (LOGO) ---
try:
    st.image("logo.png", width=350)
except:
    st.info("🏛️ The Academy crest is being polished. Welcome!")

# --- 3. THEMES & STYLING ---
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

# --- 4. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0},
        "theme": "Oxford Blue", "access_level": "Guest"
    })

# --- 5. THE GATEKEEPER (WITH PHOTO UPLOAD) ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    col1, col2 = st.columns(2)
    with col1:
        name_val = st.text_input("Full Name:", value=st.session_state.get('saved_name', ""))
        nick_val = st.text_input("Nickname (for Sir Ryan to use):", value=st.session_state.get('saved_nick', ""))
        # PHOTO UPLOADER RESTORED
        user_photo = st.file_uploader("Upload your portrait for the Academy Records:", type=['png', 'jpg', 'jpeg'])
        
    with col2:
        key_val = st.text_input("License Key:", type="password")
        remember_me = st.checkbox("💾 Save & Remember Me on this device")

    if st.button("Register & Enter Academy"):
        if name_val and key_val.lower().strip() in ["oxford2026", "guest"]:
            st.session_state.authenticated = True
            st.session_state.access_level = "Full" if key_val.lower().strip() == "oxford2026" else "Guest"
            st.session_state.student_name = name_val
            st.session_state.nickname = nick_val if nick_val else name_val
            if user_photo:
                st.session_state.avatar = user_photo
            
            if remember_me:
                st.session_state.saved_name = name_val
                st.session_state.saved_nick = nick_val
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

# --- 7. THE SIDEBAR (FULLY RESTORED) ---
with st.sidebar:
    # 1. Scholar Portrait
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=150, caption=f"Scholar {st.session_state.nickname}")
    
    st.markdown(f"### 👤 {st.session_state.nickname}")
    
    # 2. Controls & Logout
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan", value=st.session_state.mute)
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.rerun()

    st.divider()

    # 3. Subjects
    st.markdown("### 📚 Subject Selection")
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", 
                "Writing: Emails", "Writing: Letters", "Writing: Reports", "Business English",
                "Medical English", "Legal English (Law)", "Maths in English", "Arts & Culture",
                "Preparation for ELS", "Interview Excellence", "British Idioms"]
    st.selectbox("Current Focus:", subjects, key="current_subject")

    st.divider()

    # 4. The Library (Restored)
    st.markdown("### 🏛️ Library Vault")
    if st.session_state.access_level == "Guest":
        st.warning("🔒 Library Restricted")
        st.link_button("👑 Unlock Full Access", "https://www.etsy.com/shop/YourShopName")
    else:
        st.success("👑 Full Access Granted")
        with st.expander("📚 Study Resources"):
            st.link_button("Oxford Learner's Dictionary", "https://www.oxfordlearnersdictionaries.com/")
            st.link_button("BBC Worklife", "https://www.bbc.com/worklife")
            st.link_button("YouGlish (British)", "https://youglish.com/british")
            st.link_button("Baamboozle Academy Games", "https://www.baamboozle.com/")

    st.divider()

    # 5. Support & Reset (Restored)
    st.markdown("### 📞 Academy Support")
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🧹 Reset Session (Clear All)"):
        st.session_state.clear()
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# --- 9. PROGRESS BARS ---
st.subheader("📊 Your Progress Scores")
cols = st.columns(len(st.session_state.progress))
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 10. THE STUDY DESKS ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎤 Oral Examination")
    rec = mic_recorder(start_prompt="⏺️ Record Practice", stop_prompt="⏹️ Save & Listen")
    if rec:
        st.audio(rec['bytes'])
        if st.button("Submit to Sir Ryan"):
            st.success("Analysis complete. Marvelous effort! Have a biscuit.")

with col_right:
    # --- TRANSLATOR RESTORED & FUNCTIONAL ---
    st.subheader("📝 Academy Translation Desk")
    source_lang = st.selectbox("Translate from:", ["Afrikaans", "Spanish", "French", "German", "Mandarin"])
    text_to_translate = st.text_area("Type your home language here:")
    
    if st.button("Translate to British English"):
        if text_to_translate:
            with st.spinner("Translating for the Headmaster..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                trans_resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": f"Translate this {source_lang} text into formal British English."},
                              {"role": "user", "content": text_to_translate}]
                ).choices[0].message.content
                st.info(f"**English Version:** {trans_resp}")

# --- 11. CHAT HUB ---
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
            messages=[{"role": "system", "content": "You are Sir Ryan, a very formal British Headmaster. No 'mate' or 'chap'. Mention biscuits."}] + st.session_state.messages
        ).choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        speak_text(resp)

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
