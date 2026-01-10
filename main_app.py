import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")
if "theme" not in st.session_state: st.session_state.theme = "Oxford"
bg = "#FFFFFF" if st.session_state.theme == "Oxford" else "#FDF5E6"

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; }}
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {{ border: 1px solid #C5A059 !important; border-radius: 8px; }}
    .stButton>button {{ 
        background: linear-gradient(145deg, #002147, #003366); color: #C5A059; 
        border: 2px solid #C5A059; border-radius: 15px; font-weight: bold; width: 100%; height: 3.2em;
    }}
    .box {{ background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }}
    .footer {{ text-align: center; color: #888; padding: 20px; font-size: 0.8em; }}
</style>""", unsafe_allow_html=True)

# --- 2. STATE ---
items = {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "fn":"", "prog":{}, "sub":"General English", "mute":False, "vault":[], "feedback":[]}
for k, v in items.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILS ---
def logo(w=250):
    st.markdown(f"<div style='background:#002147;padding:15px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;margin:auto;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(txt):
    if st.session_state.mute: return
    try:
        p = edge_tts.Communicate(txt.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(p.save("t.mp3"))
        with open("t.mp3", "rb") as f: b = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b}">', unsafe_allow_html=True)
    except: pass

def groq_call(m, sys):
    c = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys}]+m).choices[0].message.content

# --- 4. REGISTRY ---
if not st.session_state.auth:
    logo(400); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1: fn, nk = st.text_input("Full Name:"), st.text_input("Nickname:")
    with c2: 
        if st.text_input("Key:", type="password").lower() == "oxford2026" and st.button("Enter"):
            st.session_state.auth, st.session_state.fn, st.session_state.nk = True, fn, (nk if nk else fn); st.rerun()
    st.stop()

# --- 5. LEVEL TEST (10 QUESTIONS) ---
if st.session_state.lvl == "Pending":
    logo(200); st.title("📜 Entrance Examination")
    if st.button("🎖️ Skip Assessment (Returning Student)"): 
        st.session_state.lvl = "Senior Scholar"; st.rerun()
    with st.form("exam"):
        qs = [
            ("I ___ to the shop yesterday.", ["go", "went"]), ("She ___ her tea every morning.", ["drinks", "drink"]),
            ("We ___ for three hours now.", ["have been waiting", "wait"]), ("By next year, I ___ my course.", ["will finish", "will have finished"]),
            ("If I ___ you, I would study.", ["was", "were"]), ("He doesn't like biscuits, ___ he?", ["does", "doesn't"]),
            ("The cat is sitting ___ the rug.", ["on", "at"]), ("Identify the British spelling:", ["Colour", "Color"]),
            ("Which is a formal greeting?", ["Cheers", "Dear Sir/Madam"]), ("I look forward to ___ you.", ["meeting", "meet"])
        ]
        for i, (q, opts) in enumerate(qs):
