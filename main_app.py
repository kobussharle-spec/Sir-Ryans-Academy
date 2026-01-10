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
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
    .footer { text-align: center; color: #888; font-size: 0.8em; padding: 20px; border-top: 1px solid #C5A059; margin-top: 50px; }
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
    if st.button("🎖️ Skip Assessment"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("exam"):
        qs = [("I ___ to London last week.", ["went", "go"]), ("She ___ her biscuits.", ["likes", "like"]), ("He ___ waiting since noon.", ["has been", "is"]), ("By 2027, I ___.", ["will finish", "will have finished"]), ("If I ___ rich...", ["were", "was"]), ("___ he like tea?", ["Does", "Do"]), ("Rug is ___ the floor.", ["on", "at"]), ("Spelling?", ["Colour", "Color"]), ("Greeting?", ["Dear Sir", "Hi"]), ("Look forward to ___.", ["seeing", "see"])]
        for i, (q, o) in enumerate(qs): st.radio(f"{i+1}. {q}", o, key=f"q{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    st.info(f"👤 {st.session_state
