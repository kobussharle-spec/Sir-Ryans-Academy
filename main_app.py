import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. SETUP ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background-color: #002147; color: #C5A059; border-radius: 12px; border: 1px solid #C5A059; font-weight: bold; width: 100%; }
    .stProgress > div > div > div > div { background-color: #C5A059; }
    .quiz-box { background-color: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; }
</style>""", unsafe_allow_html=True)

# --- 2. STATE ---
for k, v in {"auth":False, "msgs":[], "level":"Pending", "nick":"", "prog":0, "sub":"General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILS ---
def speak(text):
    if st.session_state.get("mute"): return
    try:
        c = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(c.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

# --- 4. LOGIN & EVAL ---
if not st.session_state.auth:
    st.title("🏛️ Academy Registry")
    fn, nk = st.text_input("Full Name:"), st.text_input("Nickname:")
    if st.text_input("Key:", type="password").lower() == "oxford2026":
        if st.button("Register"):
            st.session_state.auth, st.session_state.nick = True, (nk if nk else fn)
            st.rerun()
    st.stop()

if st.session_state.level == "Pending":
    st.title(f"📜 Evaluation: {st.session_state.nick}")
    if st.button("Skip"): st.session_state.level = "Scholar"; st.rerun()
    with st.form("ev"):
        for i in range(1, 4): st.radio(f"Q{i}", ["Option A", "Option B"], key=f"e{i}")
        if st.form_submit_button("Submit"): st.session_state.level = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("👑 Sir Ryan's")
    st.info(f"👤 {st.session_state.nick}\n🏅 {st.session_state.level}")
    st.session_state.mute = st.checkbox("Mute")
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Writing", "Business English", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        st.link_button("Oxford", "https://www.oed.com/")
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
    if st.button("Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- 6. HUB ---
st.title(f"Hub: {st.session_state.sub}")
st.progress(st.session_state.prog / 100)
st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
with st.form("qz"):
    st.radio("Spelling?", ["Honour", "Honor"])
    if st.form_submit_button("Submit"):
        st.session_state.prog = min(100, st.session_state.prog + 10)
        st.success("Correct! Have a biscuit."); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. DESKS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎤 Elocution")
    aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v27')
    if aud:
        cl = Groq(api_key=st.secrets["GROQ_API_KEY"])
        tr = cl.audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
        fb
