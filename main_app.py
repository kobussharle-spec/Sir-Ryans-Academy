import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64

# --- 1. PREMIUM AESTHETICS ---
st.set_page_config(page_title="Sir Ryan's Academy", layout="wide")
st.markdown("""<style>
    .stApp { background: white; }
    div[data-baseweb="input"], .stSelectbox { border: 1px solid #C5A059 !important; border-radius: 8px; }
    .stButton>button { background: #002147; color: #C5A059; border: 2px solid #C5A059; border-radius: 12px; font-weight: bold; width: 100%; height: 3.2em; }
    .box { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #C5A059; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

# --- 2. THE BRAIN & STATE ---
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

# --- 3. REGISTRY (PHOTO FIX) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🏛️ SIR RYAN'S ACADEMY</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fn, nk = st.text_input("Full Name"), st.text_input("Nickname")
        # Save photo to session state
        up_img = st.file_uploader("Upload Portrait", type=['png', 'jpg'])
        if up_img: st.session_state.avatar = up_img
    with c2:
        ky = st.text_input("Key", type="password")
        if st.button("Enter Academy") and ky.lower().strip() == "oxford2026":
            st.session_state.auth, st.session_state.nk = True, (nk if nk else fn); st.rerun()
    st.stop()

# --- 4. EXAM ---
if st.session_state.lvl == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🎖️ Skip Assessment"): st.session_state.lvl = "Scholar"; st.rerun()
    with st.form("exam"):
        for i in range(1, 11): st.radio(f"Q{i}: British Usage?", ["Option A", "Option B"], key=f"ex{i}")
        if st.form_submit_button("Submit"): st.session_state.lvl = "Scholar"; st.rerun()
    st.stop()

# --- 5. SIDEBAR (PHOTO DISPLAYED HERE) ---
with st.sidebar:
    st.markdown("<h2 style='color:#C5A059;'>👑 Sir Ryan's</h2>", unsafe_allow_html=True)
    if st.session_state.avatar:
        st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nk}\n🏅 Rank: {st.session_state.lvl}")
    st.session_state.mute = st.toggle("🔇 Mute Audio", value=st.session_state.mute)
    st.session_state.sub = st.selectbox("Hall:", ["General English", "Conversation", "Tenses", "Writing Emails", "Interview Prep", "🏆 GRAND FINAL"])
    with st.expander("📖 Library"):
        st.link_button("Oxford Dict", "https://www.oed.com/")
        st.link_button("Pride & Prejudice", "https://www.gutenberg.org/ebooks/1342")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

# --- 6. HUB & ELOCUTION (SIR RYAN NOW HEARS) ---
st.title(f"Academy: {st.session_state.sub}")
cp = st.session_state.prog.get(st.session_state.sub, 0)
st.progress(cp/100)

t1, t2, t3 = st.tabs(["🎙️ Study Desk", "📚 Vault", "✍️ Quiz"])
with t1:
    st.markdown("<div class='box'><h3>🎤 Elocution & Pronunciation</h3>", unsafe_allow_html=True)
    # The record button must trigger the Whisper API to "Hear" the student
    aud = mic_recorder(start_prompt="⏺️ Record Speech", stop_prompt="⏹️ Analyze", key='v40')
    if aud:
        # Step 1: Transcribe the audio
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        transcript = client.audio.transcriptions.create(file=("a.wav", aud['bytes']), model="whisper-large-v3", response_format="text")
        st.write(f"**Sir Ryan heard:** \"{transcript}\"")
        # Step 2: Sir Ryan critiques it
        critique = gcall([{"role":"user","content":transcript}], "Critique the student's English. Be British, posh, and mention if they deserve a biscuit.")
        st.info(critique); speak(critique)
    st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<div class='box'><h3>📚 Student Vault</h3>", unsafe_allow_html=True)
    up = st.file_uploader("Upload PDF:", type=['pdf'])
    if up: st.session_state.vault.append(up.name); st.success(f"{up.name} added!")
    st.write("**Archives:**", st.session_state.vault)
    st.markdown("</div>", unsafe_allow_html=True)

with t3:
    with st.form("h_qz"):
        st.radio("Correct British spelling?", ["Honour", "Honor"])
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
