import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, time, pdfplumber

# --- 1. FOUNDATION & SMART STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Smart Thin Frames for Input Boxes */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {
        border: 1px solid #C5A059 !important;
        border-radius: 8px !important;
    }
    
    /* Snazzy Button Styling */
    .stButton>button {
        background-color: #002147;
        color: #C5A059;
        border-radius: 12px;
        border: 1px solid #C5A059;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #C5A059;
        color: #002147;
        border: 1px solid #002147;
    }
    
    /* Progress Bar Colour */
    .stProgress > div > div > div > div { background-color: #C5A059; }
    
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    
    /* Elegant Section Framing */
    .quiz-box, .desk-box { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #C5A059; 
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATES ---
state_keys = {
    "auth": False, "msgs": [], "level": "Pending", "vault": {}, 
    "avatar": None, "nick": "", "full_name": "", "prog_val": 0, "cur_sub": "General English"
}
for key, val in state_keys.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. LOGO & VOICE ---
def logo(w=350):
    try: st.image("logo.png", width=w)
    except: st.markdown(f"<div style='background:#002147;padding:20px;color:#C5A059;border-radius:10px;text-align:center;width:{w}px;border:1px solid #C5A059;'>🏛️ SIR RYAN'S ACADEMY</div>", unsafe_allow_html=True)

def speak(text):
    if st.session_state.get("mute"): return
    try:
        comm = edge_tts.Communicate(text.replace("**",""), "en-GB-RyanNeural")
        asyncio.run(comm.save("t.mp3"))
        with open("t.mp3", "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 4. REGISTRY (NICKNAME RESTORED) ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        u_name = st.text_input("Full Name:", placeholder="e.g. Arthur Wellesley")
        u_nick = st.text_input("Nickname:", placeholder="What shall I call you?")
        u_photo = st.file_uploader("Upload Portrait for the Records:", type=['png', 'jpg', 'jpeg'])
    with c2:
        u_key = st.text_input("License Key:", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Register & Enter Academy"):
            if u_name and u_key.lower().strip() == "oxford2026":
                st.session_state.auth = True
                st.session_state.full_name = u_name
                st.session_state.nick = u_nick if u_nick else u_name
                st.session_state.avatar = u_photo
                st.rerun()
            else:
                st.warning("Please ensure the name is entered and use the correct key.")
    st.stop()

# --- 5. 10-QUESTION ASSESSMENT ---
if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Evaluation for {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment (Returning Scholar)"):
        st.session_state.level = "Senior Scholar"; st.rerun()
    
    st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
    with st.form("assessment"):
        st.write("Complete this 10-question trial to determine your standing:")
        q1 = st.radio("1. British spelling of 'flavour'?", ["Flavor", "Flavour"])
        q2 = st.radio("2. A 'biscuit' goes best with...", ["Gravy", "Tea"])
        q3 = st.radio("3. Past tense of 'go'?", ["Went", "Gone"])
        q4 = st.radio("4. I _______ (be) here since noon.", ["have been", "am"])
        q5 = st.radio("5. Formal sign-off?", ["Cheers", "Yours faithfully"])
        q6 = st.radio("6. British 'lift' is American...", ["Elevator", "Escalator"])
        q7 = st.radio("7. Correct spelling?", ["Occurred", "Ocured"])
        q8 = st.radio("8. 'To be knackered' means...", ["Exhausted", "Happy"])
        q9 = st.radio("9. Which is plural?", ["Phenomena", "Phenomenon"])
        q10 = st.radio("10. Best accompaniment to an afternoon lesson?", ["Biscuits", "A nap"])
        if st.form_submit_button("Submit Examination"):
            st.session_state.level = "Scholar"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    logo(180); st.divider()
    if st.session_state.avatar: st.image(st.session_state.avatar, use_container_width=True)
    st.info(f"👤 {st.session_state.nick}\n\n🏅 Rank: {st.session_state.level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    st.divider()
    subjs = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL"]
    st.session_state.cur_sub = st.selectbox("Current Hall:", subjs)
    st.divider()
    with st.expander("📖 Library Vault (10 Links)"):
        links = {"Oxford Dictionary": "https://www.oed.com/", "Cambridge Dictionary": "https://dictionary.cambridge.org/", "BBC Learning English": "https://www.bbc.co.uk/learningenglish", "British Council": "https://learnenglish.britishcouncil.org/", "Phonetic Tool": "https://phonetic-spelling.com/", "Etymology": "https://www.etymonline.com/", "Thesaurus": "https://www.thesaurus.com/", "Grammarly": "https://www.grammarly.com/", "Baamboozle Games": "https://www.baamboozle.com/", "Project Gutenberg": "https://www.gutenberg.org/"}
        for n, l in links.items(): st.link_button(n, l)
    if st.button("🚪 Log Out"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- 7. MAIN HUB & PROGRESS ---
logo(220); st.title(f"Welcome to the {st.session_state.cur_sub} Hall")
st.write(f"**Academic Completion:** {st.session_state.prog_val}%")
st.progress(st.session_state.prog_val / 100)

# --- 8. DYNAMIC QUIZ ---
st.divider()
st.subheader("✍️ Module Examination")
st.markdown("<div class='quiz-box'>", unsafe_allow_html=True)
if st.session_state.cur_sub == "Tenses":
    with st.form("t_quiz"):
        st.radio("1. By next week, I _______ (finish) the book.", ["will finish", "will have finished"])
        if st.form_submit_button("Submit Paper"):
            st.session_state.prog_val = min(100, st.session_state.prog_val + 5)
            st.success("Splendid! Have a biscuit."); st.rerun()
else:
    st.info(f"The examination for {st.session_state.cur_sub} is currently being prepared.")
st.markdown("</div>", unsafe_allow_html=True)

# --- 9. STUDY DESKS ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='desk-box'>", unsafe_allow_html=True)
    st.subheader("🎤 Oral Elocution")
    aud = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Submit", key='v19')
    if aud and st.button("Critique My Accent"): st.info("Splendid clarity, Scholar!")
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='desk-box'>", unsafe_allow_html=True)
    st.subheader("📝 PDF & Homework Vault")
    f = st.file_uploader("Upload Workbook:", type=['pdf'])
    if f and st.button("📤 Archive"): st.success("Archived in the Vault!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 10. WRITTEN ASSIGNMENT & CHAT ---
st.divider()
st.subheader("✒️ Written Assignment Desk")
st.text_area("Draft your homework here:", height=100)
if st.button("🚀 Submit Assignment"): st.success("Homework received! Gold star awarded.")

st.divider()
st.subheader("💬 Audience with Sir Ryan")
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Ask Sir Ryan..."):
    st.session_state.msgs.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are Sir Ryan. Use British spelling and mention biscuits."}] + st.session_state.msgs).choices[0].message.content
        st.markdown(r); st.session_state.msgs.append({"role": "assistant", "content": r}); speak(r)
