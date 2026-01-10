import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")
st.markdown("""<style>
    .stApp { background: white; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background: linear-gradient(145deg, #002147, #003366); color: #C5A059; border: 2px solid #C5A059; border-radius: 15px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background: #C5A059; color: #002147; }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
    .footer { text-align: center; color: #888; font-size: 0.8em; padding: 20px; }
</style>""", unsafe_allow_html=True)

# --- 2. STATE & UTILS ---
for k, v in {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "prog":{}, "sub":"General English", "mute":False, "vault":[], "feed":[]}.items():
    if k not in st.session_state: st.session_state[k] = v

def logo(w=250): st.markdown(f"<div style='background:#002147;padding:15px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;margin:auto;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(txt):
    if st.session_state.mute: return
    try:
        p = edge_tts.Communicate(txt.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(p.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

def gcall(m, sys):
    c = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys}]+m).choices[0].message.content

# --- 3. REGISTRY ---
if not st.session_state.auth:
    logo(400); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
        st.file_uploader("Upload Portrait", type=['png', 'jpg'])
    with c2:
        if st.text_input("Key", type="password").lower() == "oxford2026" and st.button("Enter"):
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- 4. LEVEL TEST ---
if st.session_state.lvl == "Pending":
    logo(200); st.title("📜 Entrance Exam")
    if st.button("🎖️ Skip Assessment (Returning Student)"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("exam"):
        qs = [("I ___ to London last week.", ["went", "go"]), ("She ___ her biscuits.", ["likes", "like"]), ("He ___ waiting since noon.", ["has been", "is"]), ("By 2027, I ___.", ["will finish", "will have finished"]), ("If I ___ rich...", ["were", "was"]), ("___ he like tea?", ["Does", "Do"]), ("Rug is ___ the floor.", ["on", "at"]), ("Spelling?", ["Colour", "Color"]), ("Greeting?", ["Dear Sir", "Hi"]), ("Look forward to ___.", ["seeing", "see"])]
        for i, (q, o) in enumerate(qs): st.radio(f"{i+1}. {q}", o, key=f"q{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    st.info(f"👤 {st.session_state.nk} | 🏅 {st.session_state.lvl}")
    st.session_state.mute = st.toggle("🔇 Mute Sir Ryan", value=st.session_state.mute)
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Conversation", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"])
    with st.expander("📖 Resources"):
        for n, u in {"Oxford Dictionary":"https://www.oed.com/", "BBC English":"https://www.bbc.co.uk/learningenglish", "Project Gutenberg":"https://www.gutenberg.org/"}.items(): st.link_button(n, u)
    if st.button("🚪 Logout"): st.session_state.clear(); st.rerun()

# --- 6. HUB ---
st.title(f"Academy Hub: {st.session_state.sub}")
cp = st.session_state.prog.get(st.session_state.sub, 0)

# --- PROGRESS BAR RESTORED ---
st.write(f"**Subject Mastery:** {cp}%")
st.progress(cp/100)

with st.expander("🧭 Orientation Guide: How to Succeed", expanded=(cp==0)):
    st.markdown(f"""
    **Welcome, Scholar {st.session_state.nk}!**
    - **Audience:** Use the chat at the bottom to ask me any questions about {st.session_state.sub}.
    - **Elocution:** Record your voice to receive my feedback on your British accent and pronunciation.
    - **Vault:** Upload your PDFs, books, or homework assignments here for safe keeping.
    - **Quiz:** Complete the examination in the 'Quiz' tab to increase your progress bar.
    """)

t1, t2, t3 = st.tabs(["🎙️ Study Desk", "📚 Vault", "✍️ Quiz"])
with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
        a = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v35')
        if a:
            t = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=("a.wav", a['bytes']), model="whisper-large-v3", response_format="text")
            f = gcall([{"role":"user","content":t}], "Critique British speech. Mention biscuits.")
            st.session_state.feed.append(f); st.info(f); speak(f)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
        tx = st.text_area("English:", height=60, key="tin")
        la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
        if st.button("Translate") and tx: st.success(gcall([{"role":"user","content":tx}], f"Translate to {la}"))
        st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    up = st.file_uploader("Upload PDF Library:", type=['pdf'])
    if up: st.session_state.vault.append(up.name); st.success(f"{up.name} added to vault!")
    st.write("**Your Vault:**", st.session_state.vault)
    st.markdown("---")
    st.write("**Recent Feedback:**")
    for fb in st.session_state.feed[-2:]: st.caption(f"Sir Ryan: {fb[:150]}...")
    st.markdown("</div>", unsafe_allow_html=True)

with t3:
    with st.form("h_qz"):
        st.radio("Which is the correct British term?", ["Flat", "Apartment"])
        if st.form_submit_button("Submit Paper"): 
            st.session_state.prog[st.session_state.sub] = min(100, cp+25); st.rerun()
