import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# Import our new modules
from styles import apply_styles
from academy_data import SUBJECTS, ENTRANCE_EXAM

apply_styles()

# --- SESSION STATE ---
for k, v in {"auth":False, "msgs":[], "lvl":"Pending", "nk":"", "prog":{}, "sub":"General English", "mute":False, "vault":[], "avatar":None}.items():
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

# --- REGISTRY ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center; color:#002147;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
        img = st.file_uploader("Upload Portrait", type=['png', 'jpg'])
        if img: st.session_state.avatar = img
    with c2:
        if st.text_input("Key", type="password").lower() == "oxford2026" and st.button("Register"):
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- ENTRANCE EXAM ---
if st.session_state.lvl == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🎖️ Skip Assessment"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("exam"):
        for i, item in enumerate(ENTRANCE_EXAM): st.radio(f"{i+1}. {item['q']}", item['o'], key=f"ex{i}")
        if st.form_submit_button("Submit Exam"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 👑 Academy Profile")
    if st.session_state.avatar: st.image(st.session_state.avatar)
    st.write(f"**Scholar:** {st.session_state.nk}")
    st.session_state.mute = st.toggle("🔇 Mute Audio", value=st.session_state.mute)
    st.session_state.sub = st.selectbox("Hall:", SUBJECTS)
    if st.button("Logout"): st.session_state.clear(); st.rerun()

# --- MAIN HUB ---
st.title(f"Academy: {st.session_state.sub}")
cp = st.session_state.prog.get(st.session_state.sub, 0)
st.progress(cp/100)

t1, t2, t3 = st.tabs(["🎙️ Study Desk", "📚 Vault", "✍️ Quiz"])
with t1:
    st.markdown("<div class='box'><h3>🎤 Elocution (Sir Ryan is listening)</h3>", unsafe_allow_html=True)
    aud = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ Analyze", key='v_final')
    if aud:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        transcript = client.audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
        st.write(f"**Sir Ryan heard:** \"{transcript}\"")
        critique = gcall([{"role":"user","content":transcript}], "You are Sir Ryan. Critique the student's pronunciation. Mention biscuits and be posh.")
        st.info(critique); speak(critique)
    st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<div class='box'><h3>📚 Student Vault</h3>", unsafe_allow_html=True)
    up = st.file_uploader("Upload PDF:", type=['pdf'])
    if up: st.session_state.vault.append(up.name); st.success(f"{up.name} added!")
    st.write(st.session_state.vault)
    st.markdown("</div>", unsafe_allow_html=True)

with t3:
    with st.form("quiz"):
        st.radio("Is it 'Cookies' or 'Biscuits'?", ["Biscuits", "Cookies"])
        if st.form_submit_button("Submit"): 
            st.session_state.prog[st.session_state.sub] = min(100, cp+25); st.rerun()

# --- CHAT & COPYRIGHT ---
st.divider()
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if p := st.chat_input("Ask Sir Ryan..."):
    st.session_state.msgs.append({"role":"user","content":p})
    with st.chat_message("user"): st.markdown(p)
    r = gcall(st.session_state.msgs, "You are Sir Ryan. Use British spelling.")
    st.session_state.msgs.append({"role":"assistant","content":r}); speak(r); st.rerun()

st.markdown("<div style='text-align:center; color:#888;'><br>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</div>", unsafe_allow_html=True)
