import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. FOUNDATION & SMART STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* The Smart Thin Frames you liked */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {
        border: 1px solid #C5A059 !important; border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #002147; color: #C5A059; border-radius: 12px;
        border: 1px solid #C5A059; font-weight: bold; width: 100%; height: 3em;
    }
    .stButton>button:hover { background-color: #C5A059; color: #002147; }
    .stProgress > div > div > div > div { background-color: #C5A059; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box, .desk-box { 
        background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
        border: 1px solid #C5A059; margin-bottom: 20px; min-height: 250px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
for k, v in {"auth": False, "msgs": [], "level": "Pending", "nick": "", "prog": 0, "sub": "General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILITIES ---
def logo(w=350):
    st.markdown(f"<div style='background:#002147;padding:20px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(text):
    if st.session_state.get("mute"): return
    try:
        c = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(c.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

# --- 4. REGISTRY PAGE (COLUMNS RESTORED) ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        fn = st.text_input("Full Name:", placeholder="e.g. Arthur Wellesley")
        nk = st.text_input("Nickname:", placeholder="The Duke")
    with c2:
        ky = st.text_input("License Key:", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Register & Enter Academy"):
            if fn and ky.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.nick = True, (nk if nk else fn)
                st.rerun()
            else: st.warning("Please enter your name and the correct key.")
    st.stop()

# --- 5. ENTRANCE EXAM ---
if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Welcome, {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment"): st.session_state.level = "Scholar"; st.rerun()
    with st.form("exam"):
        st.write("Determine your rank:")
        for i in range(1, 4): st.radio(f"Question {i}", ["Option A", "Option B"], key=f"eval_{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.level = "Scholar"; st.rerun()
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    st.info(f"👤 {st.session_state.nick}\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing", "Business English", "Legal English", "Maths", "Arts & Culture", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("Pride & Prejudice", "https://www.
