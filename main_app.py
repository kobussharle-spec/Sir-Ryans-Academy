import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. THEMES & CUSTOM SNASSY STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")

# Theme logic
if "theme" not in st.session_state: st.session_state.theme = "Oxford"
bg = "#FFFFFF" if st.session_state.theme == "Oxford" else "#FDF5E6"
btn_hv = "#C5A059" if st.session_state.theme == "Oxford" else "#002147"

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; }}
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {{ border: 1px solid #C5A059 !important; border-radius: 8px; }}
    /* Snazzy Buttons */
    .stButton>button {{ 
        background: linear-gradient(145deg, #002147, #003366); color: #C5A059; 
        border: 2px solid #C5A059; border-radius: 15px; font-weight: bold; 
        width: 100%; height: 3.2em; transition: 0.4s; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }}
    .stButton>button:hover {{ background: #C5A059; color: #002147; transform: scale(1.02); }}
    .box {{ background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }}
    .footer {{ text-align: center; color: #888; padding: 20px; font-size: 0.9em; }}
</style>""", unsafe_allow_html=True)

# --- 2. SESSION STATES ---
items = {
    "auth": False, "msgs": [], "lvl": "Pending", "nk": "", "fn": "", "prog": {}, 
    "sub": "General English", "avatar": None, "vault": [], "feedback": []
}
for k, v in items.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UTILITIES ---
def logo(w=250):
    st.markdown(f"<div style='background:#002147;padding:15px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;margin:auto;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

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

# --- 4. REGISTRY ---
if not st.session_state.auth:
    logo(400); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        fn = st.text_input("Full Name:")
        nk = st.text_input("Nickname:")
        ph = st.file_uploader("Upload Scholar Portrait:", type=['png', 'jpg'])
    with c2:
        ky = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if fn and ky.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.fn, st.session_state.nk, st.session_state.avatar = True, fn, (nk if nk else fn), ph
                st.rerun()
    st.stop()

# --- 5. ASSESSMENT ---
if st.session_state.lvl == "Pending":
    logo(200); st.title(f"📜 Evaluation: {st.session_state.nk}")
    with st.form("exam"):
        for i in range(1, 4): st.radio(f"Placement Question {i}", ["Option A", "Option B"], key=f"q{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nk}\n🏅 Rank: {st.session_state.lvl}")
    st.session_state.theme = st.selectbox("Theme:", ["Oxford", "Classic Cream"])
    if st.button("📝 Retake Level Test"): st.session_state.lvl = "Pending"; st.rerun()
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Tenses", "Grammar", "Pronunciation", "Vocabulary", "Business English", "🏆 GRAND FINAL"])
    with st.expander("📖 Library & Works"):
        st.link_button("Oxford Dict", "https://www.oed.com/"); st.link_button("BBC English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342"); st.link_button("Great Expectations", "https://www.gutenberg.org/ebooks/1400")
    if st.button("🚪 Logout"): st.session_state.clear(); st.rerun()

# --- 7. MAIN HUB ---
st.title(f"Academy Hub: {st.session_state.sub}")
cur_prog = st.session_state.prog.get(st.session_state.sub, 0)
st.write(f"**Subject Progress:** {cur_prog}%")
st.progress(cur_prog/100)

with st.expander("🎓 New Scholar's Guide", expanded=(cur_prog == 0)):
    st.write("1. **Listen** to the Headmaster. 2. **Complete** the daily Quiz. 3. **Practice** Elocution. 4. **Upload** your homework.")

# --- 8. THE STUDY DESKS ---
t1, t2, t3 = st.tabs(["🎙️ Elocution & Translator", "📚 Vault & Homework", "✍️ Module Quiz"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='box'><h3>🎤 Elocution</h3>", unsafe_allow_html=True)
        aud = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ Analyze", key='v31')
        if aud:
            tr = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
            f = groq_call([{"role":"user","content":tr}], "Critique British pronunciation. Mention biscuits.")
            st.session_state.feedback.append(f); st.info(f); speak(f)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='box'><h3>🌐 Translator</h3>", unsafe_allow_html=True)
        tx = st.text_area("English:", height=60)
        la = st.selectbox("To:", ["Spanish", "French", "German", "Chinese", "Japanese"])
        if st.button("Translate") and tx: st.success(groq_call([{"role":"user","content":tx}], f"Translate to {la}"))
        st.markdown("</div>", unsafe_allow_html=True)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='box'><h3>📝 Homework & PDF Vault</h3>", unsafe_allow_html=True)
        up = st.file_uploader("Upload PDF Books/Homework:", type=['pdf'])
        if up: st.session_state.vault.append(up.name); st.success(f"{up.name} archived!")
        st.write("**Your Archive:**", st.session_state.vault)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='box'><h3>📜 Saved Assessments</h3>", unsafe_allow_html=True)
        for fb in st.session_state.feedback[-3:]: st.caption(f"Sir Ryan: {fb[:100]}...")
        st.markdown("</div>", unsafe_allow_html=True)

with t3:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    with st.form("quiz"):
        st.radio("Correct spelling?", ["Flavour", "Flavor"])
        if st.form_submit_button("Submit"):
            st.session_state.prog[st.session_state.sub] = min(100, cur_prog + 20); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 9. CHAT & FOOTER ---
st.divider(); st.subheader("💬 Audience with Sir Ryan")
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Ask Sir Ryan..."):
    st.session_state.msgs.append({"role":"user","content":p})
    with st.chat_message("user"): st.markdown(p)
    r = groq_call(st.session_state.msgs, "You are Sir Ryan. Use British spelling.")
    st.session_state.msgs.append({"role":"assistant","content":r}); speak(r); st.rerun()

st.markdown("<div class='footer'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</div>", unsafe_allow_html=True)
