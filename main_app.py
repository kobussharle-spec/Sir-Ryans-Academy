import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, pdfplumber

# --- 1. SETUP & SMART STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px !important; }
    .stButton>button { background-color: #002147; color: #C5A059; border-radius: 12px; border: 1px solid #C5A059; font-weight: bold; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #C5A059; color: #002147; }
    .stProgress > div > div > div > div { background-color: #C5A059; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box, .desk-box { background-color: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; height: 100%; }
</style>""", unsafe_allow_html=True)

# --- 2. SESSION STATES ---
for k, v in {"auth": False, "msgs": [], "level": "Pending", "avatar": None, "nick": "", "prog": 0, "sub": "General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILITIES ---
def logo(w=350):
    st.markdown(f"<div style='background:#002147;padding:15px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(text):
    if st.session_state.get("mute"): return
    try:
        c = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(c.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

# --- 4. REGISTRY & ASSESSMENT ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        fn, nk = st.text_input("Full Name:"), st.text_input("Nickname:")
        ph = st.file_uploader("Upload Portrait:", type=['png', 'jpg'])
    with c2:
        ky = st.text_input("License Key:", type="password")
        if st.button("Register & Enter"):
            if fn and ky.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.nick, st.session_state.avatar = True, (nk if nk else fn), ph
                st.rerun()
    st.stop()

if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Evaluation: {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment"): st.session_state.level = "Senior Scholar"; st.rerun()
    with st.form("eval_form"):
        st.write("Determine your rank with this 10-question placement test:")
        for i in range(1, 11): st.radio(f"Question {i}: Identify British Usage", ["Option A", "Option B"], key=f"e_{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.level = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state
