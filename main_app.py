import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. THE ACADEMY AESTHETIC ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide", page_icon="🏛️")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { 
        background: linear-gradient(145deg, #002147, #003366); color: #C5A059; 
        border: 2px solid #C5A059; border-radius: 15px; font-weight: bold; width: 100%; height: 3em;
    }
    .stButton>button:hover { background: #C5A059; color: #002147; transform: scale(1.01); }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
</style>""", unsafe_allow_html=True)

# --- 2. THE BRAIN ---
for k, v in {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "prog":{}, "sub":"General English", "mute":False, "vault":[]}.items():
    if k not in st.session_state: st.session_state[k] = v

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
    st.markdown("<h1 style='text-align:center;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
        st.file_uploader("Upload Portrait", type=['png', 'jpg'])
    with c2:
        ky = st.text_input("License Key", type="password")
        if st.button("Enter Academy") and ky.lower().strip() == "oxford2026":
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- 4. 10-QUESTION ENTRANCE EXAM ---
if st.session_state.lvl == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🎖️ Skip Assessment"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("exam"):
        qs = [("I ___ to the shop.", ["went", "go"]), ("She ___ her tea.", ["likes", "like"]), ("They ___ waiting.", ["have been", "is"]), ("By 2027, I ___.", ["will finish", "will have finished"]), ("If I ___ you...", ["were", "was"]), ("___ he like tea?", ["Does", "Do"]), ("Rug is ___ floor.", ["on", "at"]), ("Spelling?", ["Colour", "Color"]), ("Formal?", ["Dear Sir", "Hi"]), ("Look forward to ___.", ["seeing", "see"])]
        for i, (q, o) in enumerate(qs): st.radio(f"{i+1}. {q}", o, key=f"ex{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#C5A059;'>👑 Sir Ryan's</h2>", unsafe_allow_html=True)
    st.info(f"👤 {st.session_state.nk}\n🏅 Rank: {st.session_state.lvl}")
    st.session_state.mute = st.toggle("🔇 Mute Sir Ryan", value=st.session_state.mute)
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Conversation", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
        st.link_button("Sherlock Holmes", "https://www.gutenberg.org/ebooks/1661")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

# --- 6. HUB & PROGRESS ---
st.title(f"Hall of {st.session_state.sub}")
cp = st.session_state.prog.get(st.session_state.sub, 0)
st.progress(cp/100)
st.write(f"**Mastery:** {cp}%")

t1, t2, t3 = st.tabs(["🎙️ Study Desk", "📚 Vault", "✍️ Quiz"])
with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
        aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v39')
        if aud:
            tr = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
            f = gcall([{"role":"user","content":tr}], "Critique British pronunciation. Mention biscuits.")
            st.info(f); speak(f)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
        tx = st.text_area("English:", height=65, key="tin")
        la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
        if st.button("Translate") and tx: st.success(gcall([{"role":"user","content":tx}], f"Translate to {la}"))
        st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<div class='box'><h3>📚 Student Vault</h3>", unsafe_allow_html=True)
    up = st.file_uploader("Upload PDF:", type=['pdf'])
    if up: st.session_state.vault.append(up.name); st.success(f"{up.name} added!")
    st.write("**Archives:**", st.session_state.vault)
    st.markdown("</div>", unsafe_allow_html=True)

with t3:
    with st.form("h_qz"):
        st.radio("Identify the British term:", ["Flat", "Apartment"])
        if st.form_submit_button("Submit Paper"):
            st.session_state.prog[st.session_state.sub] = min(100, cp+25); st.rerun()

# --- 7. CHAT & COPYRIGHT ---
st.divider()
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Ask Sir Ryan..."):
    st.session_state.msgs.append({"role":"user","content":p})
    with st.chat_message("user"): st.markdown(p)
    r = gcall(st.session_state.msgs, "You are Sir Ryan. Use British spelling and mention biscuits.")
    st.session_state.msgs.append({"role":"assistant","content":r}); speak(r); st.rerun()

st.markdown("<div style='text-align:center; color:#888;'><br>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</div>", unsafe_allow_html=True)
