import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, time, pdfplumber

# --- 1. FOUNDATION & SNASSY STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* Snazzy Button Styling */
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 12px;
        border: 2px solid #C5A059;
        font-weight: bold;
        height: 3em;
        width: 100%;
        transition: all 0.4s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #C5A059;
        color: #002147;
        transform: scale(1.02);
        border: 2px solid #002147;
    }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002147; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    .quiz-box { background-color: #f9f9f9; padding: 25px; border-radius: 15px; border: 2px solid #002147; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
state_keys = {
    "auth": False, "msgs": [], "level": "Pending", "vault": {}, 
    "avatar": None, "nick": "Scholar", "skip_test": False
}
for key, val in state_keys.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. VOICE ENGINE ---
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
    except: st.markdown(f"<div style='background:#002147;padding:20px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:2px solid #C5A059;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

# --- 4. REGISTRY ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name:")
        nick = st.text_input("Nickname:")
        photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        key = st.text_input("License Key:", type="password")
        if st.button("Register & Proceed"):
            if name and key.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.nick, st.session_state.avatar = True, (nick if nick else name), photo
                st.rerun()
    st.stop()

# --- 5. 10-QUESTION ASSESSMENT & SKIP OPTION ---
if st.session_state.level == "Pending":
    logo(200); st.title("📜 Entrance Evaluation")
    
    col_skip, _ = st.columns([1, 2])
    with col_skip:
        if st.button("🎖️ Returning Student? Skip to Hub"):
            st.session_state.level = "Senior Scholar"
            st.rerun()

    st.markdown("---")
    with st.form("assessment_form"):
        st.write("Complete the 10-question evaluation to determine your rank:")
        q1 = st.radio("1. British spelling of 'color'?", ["Color", "Colour"])
        q2 = st.radio("2. A 'biscuit' is a...", ["Cookie", "Scone"])
        q3 = st.radio("3. Correct tense: I _______ (see) him yesterday.", ["have seen", "saw"])
        q4 = st.radio("4. Formal greeting?", ["Hiya!", "Good morning, Sir."])
        q5 = st.radio("5. 'To be chuffed' is to be...", ["Happy", "Angry"])
        q6 = st.radio("6. Proper spelling?", ["Honour", "Honor"])
        q7 = st.radio("7. I _______ (wait) for an hour.", ["am waiting", "have been waiting"])
        q8 = st.radio("8. A 'boot' of a car is the...", ["Trunk", "Hood"])
        q9 = st.radio("9. Which is correct?", ["Whose bag is this?", "Who's bag is this?"])
        q10 = st.radio("10. 'It's raining cats and _______'", ["Dogs", "Biscuits"])
        
        if st.form_submit_button("Submit Examination"):
            st.session_state.level = "Scholar"
            st.success("Splendid effort! Welcome to the Academy.")
            st.rerun()
    st.stop()

# --- 6. SIDEBAR (15 SUBJECTS & 10 LINKS) ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nick}\n\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    subjs = [
        "General English", "Tenses", "Grammar Mastery", "Pronunciation", 
        "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", 
        "Business English", "Legal English", "Maths", "Arts & Culture", 
        "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"
    ]
    st.session_state.cur_sub = st.selectbox("Focus Area:", subjs)

    st.divider()
    with st.expander("📖 Library Vault (10 Resources)"):
        st.link_button("Oxford Dictionary", "https://www.oed.com/")
        st.link_button("Cambridge Dictionary", "https://dictionary.cambridge.org/")
        st.link_button("BBC Learning English", "https://www.bbc.co.uk/learningenglish")
        st.link_button("British Council Learn", "https://learnenglish.britishcouncil.org/")
        st.link_button("Phonetic Spelling Tool", "https://phonetic-spelling.com/")
        st.link_button("Etymology Online", "https://www.etymonline.com/")
        st.link_button("Thesaurus.com", "https://www.thesaurus.com/")
        st.link_button("Grammarly", "https://www.grammarly.com/")
        st.link_button("Baamboozle Games", "https://www.baamboozle.com/")
        st.link_button("Project Gutenberg", "https://www.gutenberg.org/")

    if st.button("🚪 Log Out"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- 7. MAIN HUB ---
logo(220); st.title(f"Academy Hub: {st.session_state.cur_sub}")

st.divider()
st.subheader("✍️ Module Examination")
with st.container():
    st.markdown(f"<div class='quiz-box'><strong>Hall: {st.session_state.cur_sub}</strong>", unsafe_allow_html=True)
    if st.session_state.cur_sub == "Tenses":
        with st.form("t_quiz"):
            st.radio("1. I _______ (finish) my work by 5pm tomorrow.", ["will finish", "will have finished"])
            if st.form_submit_button("Submit Exam"): st.success("Paper submitted! You deserve a biscuit.")
    else: st.write("Exam paper is being drafted by the faculty.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎤 Oral Elocution")
    aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Submit", key='v17')
    if aud and st.button("Critique My Speech"):
        st.info("Sir Ryan is listening... Splendid clarity!")

with c2:
    st.subheader("📝 PDF & Homework Vault")
    f = st.file_uploader("Upload PDF:", type=['pdf'])
    if f and st.button("📤 Archive to Vault"):
        with pdfplumber.open(f) as pdf: txt = "".join([p.extract_text() for p in pdf.pages])
        st.session_state.vault[f.name] = txt
        st.success("Archived!")

st.divider()
st.subheader("✒️ Written Assignment Desk")
st.text_area("Draft your essay here:", height=150, placeholder="Start writing, Scholar...")
if st.button("🚀 Submit Homework"): st.success("Well done! Gold star awarded.")

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
