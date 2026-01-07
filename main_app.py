import streamlit as st
from groq import Groq
import pypdf
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import requests
import urllib.parse
import pandas as pd

# --- 1. THE FOUNDATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓", layout="wide")

# --- 2. EXECUTIVE THEME (Oxford Blue & High Visibility) ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #002147 !important; min-width: 350px; }
    
    /* High Visibility Sidebar Text */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] li, [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }

    /* Gold Professional Buttons */
    .stButton>button { 
        background-color: #C5A059 !important; 
        color: #002147 !important; 
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100%;
        border: none !important;
    }
    .stButton>button:hover { background-color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATES ---
initial_states = {
    "authenticated": False, "messages": [], "merits": 0, "gradebook": [], 
    "student_name": "Scholar", "pdf_text": "", "streak_count": 1, 
    "last_visit": datetime.date.today(), "english_level": None,
    "current_subject": "General Knowledge", "homework_task": None
}
for key, val in initial_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. THE GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Executive Academy")
    name_input = st.text_input("Name for the Register:")
    license_key = st.text_input("License Key:", type="password")
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.rerun()
        else: st.error("Access Denied, old sport.")
    st.stop()

# --- 5. SIR RYAN'S VOICE ENGINE ---
def speak_text(text):
    try:
        clean = text.replace("**", "").replace("#", "").replace("_", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        # Direct async execution to ensure voice plays
        asyncio.run(communicate.save("v.mp3"))
        with open("v.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error(f"Voice error: {e}")

# --- 6. WELCOME LETTER COMPONENT ---
def show_welcome_letter():
    st.markdown(f"""
    <div style="border: 3px solid #C5A059; padding: 25px; border-radius: 15px; background-color: #ffffff; color: #002147; font-family: 'Times New Roman', serif;">
        <h2 style="text-align: center; color: #002147;">📜 A Note from the Headmaster</h2>
        <p><b>To the Honourable {st.session_state.student_name},</b></p>
        <p>It is with great pleasure that I welcome you to <b>Sir Ryan's Executive Academy</b>. You have shown a commendable spirit by choosing this path of professional mastery.</p>
        <p>Within these digital halls, we value precision, the <b>STAR Method</b>, and the occasional <b>biscuit</b>. Whether you are here for Interview Prep or to master the King's English, I am here to guide you.</p>
        <p><i>Warmest Regards,</i><br><b>Sir Ryan</b><br>Headmaster</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# --- 7. THE COMPREHENSIVE SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ffffff/university.png", width=80)
    st.title("🏫 Academy Registry")
    
    # 7.1 SUBJECT REGISTRY (The Full List)
    st.header("📚 Subject Registry")
    subject_list = [
        "English: Tenses", "English: Grammar", "English: Pronunciation",
        "English: Vocabulary", "English: Conversation", 
        "English: Writing - Emails", "English: Writing - Letters", "English: Writing - Reports",
        "Preparing for ELS", "Interview Prep (STAR Method)", "Business English", "General Knowledge"
    ]
    st.session_state.current_subject = st.selectbox("Current Focus:", subject_list)

    # 7.2 ACADEMY LIBRARY (PDF Uploader)
    st.header("📜 Academy Library")
    uploaded_file = st.file_uploader("Upload Course PDF", type="pdf")
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
        st.success("Workbook Filed Successfully!")

    # 7.3 HANDBOOK & GUIDANCE
    with st.expander("📖 How to Use the Academy"):
        st.write("""
        1. **Archives:** Upload your PDF in the Library.
        2. **Focus:** Select your subject from the Registry.
        3. **Dialogue:** Ask Sir Ryan anything in the Study Hall.
        4. **Voice:** Use the Oral Exam for feedback.
        """)

    # 7.4 RESOURCES & EXTRAS
    with st.expander("🏛️ Resources & Idioms"):
        st.write("* **British Idioms:** 'Chuffed to bits', 'Spot of bother'.")
        st.write("* **Dictionary:** Use 'Ask Sir Ryan' for definitions.")
        try:
            weather = requests.get("https://wttr.in/London?format=%c+%t").text
            st.info(f"🇬🇧 London Weather: {weather}")
        except: pass

    # 7.5 PRIVACY & POLICY
    with st.expander("🔒 Privacy & Honour Code"):
        st.write("Your data remains in this session. We follow the 2026/2027 Executive Privacy Standards.")

    # 7.6 STUDENT RECORDS (Gradebook)
    st.header("📜 Student Gradebook")
    if st.session_state.gradebook:
        st.table(pd.DataFrame(st.session_state.gradebook))
    else: st.write("No grades recorded yet.")

    # 7.7 CONTACT & FOOTER
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    if st.button("🧹 Reset Academy Session"):
        st.session_state.clear()
        st.rerun()
    st.caption("© 2026 J Steenekamp | Sir Ryan's Academy")

# ---
