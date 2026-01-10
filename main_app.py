import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. STYLE & SETUP ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background: #002147; color: #C5A059; border: 1px solid #C5A059; border-radius: 12px; font-weight: bold; width: 100%; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

# --- 2. STATE ---
for k, v in {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "prog":0, "sub":"General English"}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILS ---
def speak(txt):
    if st.session_state.get("mute"): return
    try:
        p = edge_tts.Communicate(txt.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(p.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

def groq_chat(m, sys):
    c = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys}]+m).choices[0].message.content

# --- 4. REGISTRY ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
    with c2: 
        if st.text_input("Key", type="password").lower() == "oxford2026" and st.button("Enter Academy"):
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- 5. EXAM ---
if st.session_state.lvl == "Pending":
    st.title(f"📜 Welcome, {st.session_state.nk}")
    if st.button("Skip to Hub"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("ex"):
        for i in range(1,11): st.radio(f"Question {i}", ["Option A", "Option B"], key=f"q{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("👑 Sir Ryan's")
    st.info(f"👤 {st.session_state.nk}\n🏅 {st.session_state.lvl}")
    st.session_state.mute = st.checkbox("Mute Sir Ryan")
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Emails", "Letters", "Reports", "Business", "Legal", "Maths", "Arts", "ELS", "Interview", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        st.link_button("Oxford", "https://www.oed.com/"); st.link_button("Holmes", "https://www.gutenberg.org/ebooks/1661")
    if st.button("Logout"): 
        st.session_state.clear(); st.rerun()

# --- 7. HUB ---
st.title(f"Hall of {st.session_state.sub}")
st.progress(st.session_state.prog/100)
with st.container():
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    with st.form("qz"):
        st.radio("Correct spelling?", ["Honour", "Honor"])
        if st.form_submit_button("Submit Paper"):
            st.session_state.prog = min(100, st.session_state.prog+10); st.success("Splendid! Have a biscuit."); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 8. DESKS ---
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
    a = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v30')
    if a:
        t = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=("a.wav", a['bytes']), model="whisper-large-v3", response_format="text")
        f = groq_chat([{"role":"user","content":t}], "Critique pronunciation like Sir Ryan. Be British. Mention biscuits.")
        st.info(f); speak(f)
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
    tx = st.text_area("English:", height=70)
    la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
    if st.button("Translate Now") and tx:
        st.success(groq_chat([{"role":"user","content":tx}], f"Translate to {la}"))
    st.markdown("</div>", unsafe_allow_html=True)

# --- 9. CHAT & FOOTER ---
st.divider(); st.subheader("💬 Audience with Sir Ryan")
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Ask..."):
    st.session_state.msgs.append({"role":"user","content":p})
    with st.chat_message("user"): st.markdown(p)
    r = groq_chat(st.session_state.msgs, "You are Sir Ryan. Use British spelling.")
    st.session_state.msgs.append({"role":"assistant","content":r}); speak(r); st.rerun()
st.markdown("<center>© 2026 J Steenekamp | Sir Ryan's Academy</center>", unsafe_allow_html=True)
