import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. THE ACADEMY AESTHETIC ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background: #002147; color: #C5A059; border: 1px solid #C5A059; border-radius: 12px; font-weight: bold; width: 100%; height: 3em; }
    .stButton>button:hover { background: #C5A059; color: #002147; }
    .stProgress > div > div > div > div { background-color: #C5A059; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; min-height: 250px; }
</style>""", unsafe_allow_html=True)

# --- 2. ACADEMY BRAIN ---
for k, v in {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "prog":0, "sub":"General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

def speak(txt):
    if st.session_state.get("mute"): return
    try:
        p = edge_tts.Communicate(txt.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(p.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

def groq_call(m, sys):
    c = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys}]+m).choices[0].message.content

# --- 3. REGISTRY (COLUMNS RESTORED) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fn = st.text_input("Full Name:", placeholder="Arthur Wellesley")
        nk = st.text_input("Nickname:", placeholder="The Duke")
    with c2:
        ky = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if fn and ky.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
            else: st.warning("Registration requires a Name and the key 'oxford2026'.")
    st.stop()

# --- 4. ENTRANCE EVALUATION ---
if st.session_state.lvl == "Pending":
    st.title(f"📜 Welcome to the Hall of Records, {st.session_state.nk}")
    if st.button("🎖️ Skip Assessment (Veteran Status)"): st.session_state.lvl = "Senior Scholar"; st.rerun()
    with st.form("exam"):
        st.write("Complete this 10-question placement test:")
        for i in range(1, 11): st.radio(f"Q{i}: British Usage?", ["Option A", "Option B"], key=f"q{i}")
        if st.form_submit_button("Submit Examination"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#C5A059;'>👑 Sir Ryan's</h2>", unsafe_allow_html=True)
    st.info(f"👤 {st.session_state.nk}\n🏅 Rank: {st.session_state.lvl}")
    st.session_state.mute = st.checkbox("🔇 Mute Audio")
    st.session_state.sub = st.selectbox("Current Hall:", ["General English", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Business English", "Legal English", "Maths", "Arts & Culture", "🏆 GRAND FINAL"])
    with st.expander("📖 Library & Classics"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
        st.link_button("Sherlock Holmes", "https://www.gutenberg.org/ebooks/1661")
    if st.button("🚪 Logout"): st.session_state.clear(); st.rerun()

# --- 6. MAIN HUB ---
st.title(f"Hall of {st.session_state.sub}")
st
