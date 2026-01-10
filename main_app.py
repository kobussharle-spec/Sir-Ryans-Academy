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
        if st.text_input("License Key:", type="password").lower().strip() == "oxford2026":
            if st.button("Register & Enter"):
                st.session_state.auth, st.session_state.nick, st.session_state.avatar = True, (nk if nk else fn), ph
                st.rerun()
    st.stop()

if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Evaluation: {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment"): st.session_state.level = "Senior Scholar"; st.rerun()
    with st.form("eval_f"):
        for i in range(1, 11): st.radio(f"Q{i}: British Usage?", ["A", "B"], key=f"e_{i}")
        if st.form_submit_button("Submit"): st.session_state.level = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nick}\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        lns = {"Oxford": "https://www.oed.com/", "BBC": "https://www.bbc.co.uk/learningenglish", "Gutenberg": "https://www.gutenberg.org/"}
        for n, l in lns.items(): st.link_button(n, l)
    with st.expander("📚 Classics"):
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
        st.link_button("Sherlock Holmes", "https://www.gutenberg.org/ebooks/1661")
    if st.button("🚪 Log Out"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- 6. HUB ---
logo(220); st.title(f"Hub: {st.session_state.sub}")
st.progress(st.session_state.prog / 100)

st.divider(); st.subheader("✍️ Examination Hall")
with st.container():
    st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
    with st.form("h_q"):
        st.radio("Correct spelling?", ["Colour", "Color"])
        if st.form_submit_button("Submit Exam"):
            st.session_state.prog = min(100, st.session_state.prog + 10)
            st.success("Correct! Enjoy a biscuit."); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. DESKS ---
st.divider(); col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='desk-box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
    aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v25')
    if aud:
        cl = Groq(api_key=st.secrets["GROQ_API_KEY"])
        tr = cl.audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
        fb = cl.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "Critique pronunciation like Sir Ryan. Be British."},{"role": "user", "content": tr}]).choices[0].message.content
        st.info(fb); speak(fb)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='desk-box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
    tx = st.text_area("English:", placeholder="Type here...", height=60)
    la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
    if st.button("Translate"):
        cl = Groq(api_key=st.secrets["GROQ_API_KEY"])
        st.success(cl.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Translate to {la}"},{"role": "user", "content": tx}]).choices[0].message.content)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='desk-box'><h3>📝 Vault</h3>", unsafe_allow_html=True)
    if st.file_uploader("Upload PDF:", type=['pdf']): st.success("Archived!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 8. CHAT ---
st.divider(); st.subheader("💬 Audience with Sir Ryan")
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Ask...
