import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, time, pdfplumber

# --- 1. SETUP & STYLE ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { background-color: #002147; color: #C5A059; border-radius: 20px; font-weight: bold; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #002147; }
    .quiz-box { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #C5A059; }
</style>""", unsafe_allow_html=True)

# --- 2. STATES & VOICE ---
for key in ["auth", "msgs", "level", "vault", "avatar", "prog"]:
    if key not in st.session_state:
        st.session_state[key] = False if key=="auth" else [] if key=="msgs" else "Pending" if key=="level" else {} if key=="vault" else None if key=="avatar" else {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0}

def speak(text):
    if st.session_state.get("mute"): return
    try:
        comm = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(comm.save("t.mp3"))
        with open("t.mp3", "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

def logo(w=350):
    try: st.image("logo.png", width=w)
    except: st.markdown(f"<div style='background:#002147;padding:10px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

# --- 3. REGISTRY & EVALUATION ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name:")
        nick = st.text_input("Nickname:")
        photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg'])
    with c2:
        key = st.text_input("License Key:", type="password")
        if st.button("Register & Begin"):
            if name and key.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.nick, st.session_state.avatar = True, (nick if nick else name), photo
                st.rerun()
    st.stop()

if st.session_state.level == "Pending":
    logo(200); st.title("📜 Entrance Evaluation")
    with st.form("eval"):
        q1 = st.radio("Correct British spelling?", ["Color", "Colour"])
        q2 = st.radio("A 'biscuit' is a...", ["Cookie", "Muffin"])
        if st.form_submit_button("Enter Academy"):
            st.session_state.level = "Senior Scholar"
            st.rerun()
    st.stop()

# --- 4. SIDEBAR (SUBJECTS & LINKS) ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nick}\n\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.divider()
    subjs = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"]
    st.session_state.cur_sub = st.selectbox("Focus Area:", subjs)
    st.divider()
    with st.expander("📖 Library Vault"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("Phonetic Spelling", "https://phonetic-spelling.com/")
        st.link_button("Baamboozle", "https://www.baamboozle.com/")
    if st.button("🚪 Log Out"):
        st.session_state.auth = False
        st.rerun()

# --- 5. MAIN HUB ---
logo(220); st.title(f"Welcome to the {st.session_state.cur_sub} Hall")
cols = st.columns(4)
for i, (s, v) in enumerate(st.session_state.prog.items()): cols[i].metric(s, f"{v}%")

st.divider()
st.subheader("✍️ Module Examination")
with st.container():
    st.markdown(f"<div class='quiz-box'><strong>Hall: {st.session_state.cur_sub}</strong>", unsafe_allow_html=True)
    if st.session_state.cur_sub == "Tenses":
        with st.form("quiz"):
            ans = st.radio("I _______ (work) here for years.", ["work", "have been working"])
            if st.form_submit_button("Submit"):
                st.success("Splendid! Have a biscuit."); st.session_state.prog["Tenses"] = 25
    else: st.write("Exam paper is being drafted.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎤 Oral Elocution")
    aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Submit", key='v16')
    if aud and st.button("Critique"):
        st.info("Analysis: Your elocution is developing beautifully!")
with c2:
    st.subheader("📝 PDF & Homework Vault")
    f = st.file_uploader("Upload PDF:", type=['pdf'])
    if f and st.button("Archive"):
        with pdfplumber.open(f) as pdf: txt = "".join([p.extract_text() for p in pdf.pages])
        st.session_state.vault[f.name] = txt
        st.success("Archived!")

st.divider()
st.subheader("✒️ Written Assignment Desk")
st.text_area("Draft your essay here:", height=100)
if st.button("🚀 Submit Homework"): st.success("Well done! A gold star for you.")

st.divider()
st.subheader("💬 Audience with the Headmaster")
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Ask Sir Ryan..."):
    st.session_state.msgs.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Use British spelling and mention biscuits."}] + st.session_state.msgs).choices[0].message.content
        st.markdown(r); st.session_state.msgs.append({"role": "assistant", "content": r}); speak(r)

st.markdown("<br><hr><center>© 2026 J Steenekamp | Sir Ryan's Academy</center>", unsafe_allow_html=True)
