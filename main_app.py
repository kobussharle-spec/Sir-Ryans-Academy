import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts, asyncio, base64, time, pdfplumber

# --- 1. FOUNDATION & SMART STYLING ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Smart Thin Gold Frames for Inputs */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stSelectbox {
        border: 1px solid #C5A059 !important;
        border-radius: 8px !important;
    }
    
    /* Snazzy Oxford Buttons */
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
    
    .stProgress > div > div > div > div { background-color: #C5A059; }
    h1, h2, h3 { color: #002147; font-family: 'Times New Roman'; }
    
    .quiz-box, .desk-box { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #C5A059; 
        margin-bottom: 20px;
    }
    footer { visibility: hidden; }
    .copyright { text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; }
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

# --- 4. REGISTRY ---
if not st.session_state.auth:
    logo(); st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        u_name = st.text_input("Full Name:", placeholder="e.g. Jane Austen")
        u_nick = st.text_input("Nickname:", placeholder="How shall I address you?")
        u_photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        u_key = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if u_name and u_key.lower().strip() == "oxford2026":
                st.session_state.auth, st.session_state.full_name, st.session_state.nick, st.session_state.avatar = True, u_name, (u_nick if u_nick else u_name), u_photo
                st.rerun()
    st.stop()

# --- 5. EVALUATION ---
if st.session_state.level == "Pending":
    logo(200); st.title(f"📜 Welcome, Scholar {st.session_state.nick}")
    if st.button("🎖️ Skip Assessment (Veteran Student)"):
        st.session_state.level = "Senior Scholar"; st.rerun()
    with st.form("assessment"):
        st.write("Determine your rank with this 10-question evaluation:")
        st.radio("1. British spelling?", ["Flavour", "Flavor"], key="q1")
        st.radio("2. A 'biscuit' is usually...", ["Crunchy", "Soft and bready"], key="q2")
        # Add more questions here as needed
        if st.form_submit_button("Submit Exam"):
            st.session_state.level = "Scholar"; st.rerun()
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
    
    with st.expander("📚 Great Works Reading Room"):
        st.link_button("Pride and Prejudice", "https://www.gutenberg.org/ebooks/1342")
        st.link_button("Great Expectations", "https://www.gutenberg.org/ebooks/1400")
        st.link_button("Sherlock Holmes", "https://www.
