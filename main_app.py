import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, time, pdfplumber

# --- 1. FOUNDATION & SMART STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {
        border: 1px solid #C5A059 !important; border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #002147; color: #C5A059; border-radius: 12px;
        border: 1px solid #C5A059; font-weight: bold; transition: 0.3s;
        width: 100%; height: 3em;
    }
    .stButton>button:hover { background-color: #C5A059; color: #002147; border: 1px solid #002147; }
    .stProgress > div > div > div > div { background-color: #C5A059; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box, .desk-box { 
        background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
        border: 1px solid #C5A059; margin-bottom: 20px; height: 100%;
    }
    .copyright { text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
for k, v in {"auth": False, "msgs": [], "level": "Pending", "vault": {}, "avatar": None, "nick": "", "fn": "", "prog": 0, "sub": "General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILITIES ---
def logo(w=350):
    try: st.image("logo.png", width=w)
    except: st.markdown(f"<div style='background:#002147;padding:20px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(text):
    if st.session_state.get("mute"): return
    try:
        c = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(c.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

# --- 4. REGISTRY ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        u_fn, u_nk = st.text_input("Full Name:"), st.text_input("Nickname:")
        u_ph = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        u_ky = st.text_input("License Key:", type="password")
        if st.button("Register & Enter"):
            if u_fn and u_ky.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.fn, st.session_state.nick, st.session_state.avatar = True, u_fn, (u_nk if u_nk else u_fn), u_ph
                st.rerun()
    st.stop()

# --- 5. ASSESSMENT ---
if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Evaluation: {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment"):
        st.session_state.level = "Senior Scholar"; st.rerun()
    with st.form("eval"):
        st.write("10 Question Placement Test")
        for i in range(1, 11): st.radio(f"Question {i}", ["Option A", "Option B"], key=f"q_{i}")
        if st.form_submit_button("Submit"):
            st.session_state.level = "Scholar"; st.rerun()
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nick}\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.divider()
    subjs = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"]
    st.session_state.sub = st.selectbox("Current Hall:", subjs)
    with st.expander("📖 Library"):
        lns = {"Oxford": "https://www.oed.com/", "Cambridge": "https://dictionary.cambridge.org/", "BBC": "https://www.bbc.co.uk/learningenglish", "British Council": "https://learnenglish.britishcouncil.org/", "Phonetics": "https://phonetic-spelling.com/", "Etymology": "https://www.etymonline.com/", "Thesaurus": "https://www.thesaurus.com/", "Grammarly": "https://www.grammarly.com/", "Baamboozle": "https://www.baamboozle.com/", "Gutenberg": "https://www.gutenberg.org/"}
        for n, l in lns.items(): st.link_button(n, l)
    with st.expander("📚 Great Works"):
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
        st.link_button("Great Expectations", "https://www.gutenberg.org/ebooks/1400")
        st.link_button("Sherlock Holmes", "https://www.gutenberg.org/ebooks/1661")
    if st.button("🚪 Log Out"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- 7. HUB & PROGRESS ---
logo(220); st.title(f"Academy Hub: {st.session_state.sub}")
st.write(f"**Academic Completion:** {st.session_state.prog}%")
st.progress(st.session_state.prog / 100)

# --- 8. QUIZ ---
st.divider(); st.subheader("✍️ Module Examination")
st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
with st.form("h_quiz"):
    st.radio("1. Which spelling is correct?", ["Honour", "Honor"])
    if st.form_
