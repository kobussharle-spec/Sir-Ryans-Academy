import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. THE ACADEMY AESTHETIC ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background: #002147; color: #C5A059; border: 1px solid #C5A059; border-radius: 12px; font-weight: bold; width: 100%; }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
</style>""", unsafe_allow_html=True)

# --- 2. THE ACADEMY BRAIN ---
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

# --- 3. THE REGISTRY ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
    with c2: 
        if st.text_input("Key", type="password").lower() == "oxford2026" and st.button("Enter Academy"):
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- 4. THE HUB & SIDEBAR ---
with st.sidebar:
    st.title("👑 Sir Ryan's")
    st.info(f"👤 {st.session_state.nk}\n🏅 Level: {st.session_state.lvl}")
    st.session_state.mute = st.checkbox("Mute Sir Ryan")
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Business English", "🏆 GRAND FINAL"])
    if st.button("Logout"): st.session_state.clear(); st.rerun()

st.title(f"Hall of {st.session_state.sub}")
st.progress(st.session_state.prog/100)

# --- 5. THE STUDY DESKS ---
d1, d2 = st.columns(2)
with d1:
    st.markdown("<div class='box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
    a = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Analyze", key='v_final')
    if a:
        t = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=("a.wav", a['bytes']), model="whisper-large-v3", response_format="text")
        f = groq_call([{"role":"user","content":t}], "Critique British pronunciation. Mention biscuits.")
        st.info(f); speak(f)
    st.markdown("</div>", unsafe_allow_html=True)
with d2:
    st.markdown("<div class='box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
    tx = st.text_area("English:", height=65)
    la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
    if st.button("Translate") and tx:
        st.success(groq_call([{"role":"user","content":tx}], f"Translate to {la}"))
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. AUDIENCE WITH SIR RYAN ---
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Speak to the Headmaster..."):
    st.session_state.msgs.append({"role":"user","content":p})
    with st.chat_message("user"): st.markdown(p)
    r = groq_call(st.session_state.msgs, "You are Sir Ryan. Use British spelling.")
    st.session_state.msgs.append({"role":"assistant","content":r}); speak(r); st.rerun()
