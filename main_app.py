import streamlit as st
from groq import Groq
import PyPDF2
import pypdf # Ensure you have this for the reader
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import requests
import urllib.parse
import pandas as pd
from io import BytesIO

# --- 1. THE FOUNDATION (MUST BE FIRST) ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# --- 2. THE THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #002147 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: white !important; }
    .stButton>button { background-color: #C5A059 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gradebook" not in st.session_state:
    st.session_state.gradebook = []
# (Add any other essential keys here)

# --- 4. THE ONLY GATE ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Academy")
    
    name_input = st.text_input("Please enter your name for the Academy Register:")
    license_key = st.text_input("Enter your License Key:", type="password")
    
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.success("Access Granted. Welcome, old sport!")
            st.rerun()
        else:
            st.error("I'm afraid that key doesn't fit the lock.")
    st.stop() # THE APP STOPS HERE UNTIL AUTHENTICATED

# --- 5. THE REST OF THE ACADEMY ---
# Put all your functions (speak_text, etc.) and sidebar code below here!
# --- 1. PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# Initialize all session states
initial_states = {
    "authenticated": False,
    "student_name": "Scholar",
    "name": "Student",
    "english_level": None,
    "vocab_bank": [],
    "homework_history": [],
    "messages": [],
    "merits": 0,
    "graduated": False,
    "needs_intro": False,
    "homework_task": None,
    "streak_count": 1,
    "last_visit_date": datetime.date.today(),
    "gradebook": [],
    "current_subject": "General Knowledge"
}

for key, value in initial_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. VOICE & HELPER FUNCTIONS ---
def speak_text(text):
    clean_text = text.replace("**", "").replace(":", ".").replace("_", "").replace("#", "")
    filename = "academy_voice.mp3"
    try:
        communicate = edge_tts.Communicate(clean_text, "en-GB-RyanNeural")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(communicate.save(filename))
        loop.close()
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        audio_id = str(time.time())
        audio_html = f'<audio autoplay="true" key="{audio_id}"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.warning(f"Sir Ryan's voice is a bit hoarse: {e}")

def show_welcome_letter():
    st.markdown(f"""
    <div style="border: 2px solid #002366; padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
    <h3>📜 A Personal Note from the Headmaster</h3>
    <p><b>To the Honourable {st.session_state.student_name},</b></p>
    <p>It is with great pride that I welcome you to <b>Sir Ryan's Academy</b>. You have chosen a path of 
    excellence, and I am delighted to oversee your journey through the vast landscapes of 
    {st.session_state.current_subject}.</p>
    <p>In these halls, we value precision, dedication, and the occasional <b>biscuit</b> during study breaks. 
    Whether you are here to master the intricacies of <b>English Grammar</b> or to prepare for the 
    rigours of <b>Medicine</b>, know that my door—and the Examination Hall—is always open.</p>
    <p><i>Signed,</i><br><b>Sir Ryan</b> Headmaster, The Academy</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #002366;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #003399;
        color: #FFD700;
    }
    </style>
""", unsafe_allow_html=True)

import streamlit as st
# ... keep all your other imports ...

# --- 1. PAGE CONFIG MUST BE THE VERY FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# --- 2. THE STABLE EXECUTIVE THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #002147 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: white !important; }
    .stButton>button { background-color: #C5A059 !important; color: white !important; border-radius: 4px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALIZE SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
# ... (Keep your other initial_states here) ...

# --- 4. THE SINGLE UNIFIED GATE ---
if not st.session_state.authenticated:
    st.title("🏛️ Welcome to Sir Ryan's Academy")
    st.info("Please present your credentials to enter the Study Hub.")
    
    name_input = st.text_input("Please enter your name for the Academy Register:", placeholder="e.g. Master John")
    license_key = st.text_input("Enter your License Key (from Etsy):", type="password")
    
    if st.button("Unlock the Study Hub"):
        # We will use your preferred key: Oxford2026
        if license_key == "Oxford2026" and name_input:
            st.session_state.authenticated = True
            st.session_state.student_name = name_input
            st.success(f"Welcome, {name_input}! Opening the gates...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("I'm afraid that key doesn't fit the lock, old sport.")
    st.stop() # This ensures nothing below runs until they are authenticated

# --- 5. THE REST OF YOUR ACADEMY CODE ---
# (Everything else: speak_text, show_welcome_letter, sidebar, etc., goes here!)

# --- 5. THE ACADEMY SIDEBAR (FULL RESTORATION) ---
with st.sidebar:
    st.title("🏫 Academy Controls")

with st.sidebar:
    st.header("📖 Academy Handbook")
    with st.expander("How to Use the Academy (All Ages)", expanded=True):
        st.write("""
        1. **The Library:** Put your workbook here so Sir Ryan can read it.
        2. **Fresh Start:** If you close the page, the library clears. You'll need to put the book back in next time.
        3. **Internet:** You need to be connected to the web for Sir Ryan to 'think' and 'speak.'
        4. **Talking to Sir Ryan:** Type your message and press 'Enter.' He is very polite and helpful!
        5. **Safety:** This is a safe place for everyone. Please use kind words and professional language.
        """)
    
    # Gradebook
    st.header("📜 Student Gradebook")
    if not st.session_state.gradebook:
        st.write("No grades recorded yet.")
    else:
        st.table(pd.DataFrame(st.session_state.gradebook))
    
    st.divider()
    
    # Subject Selection
    st.header("📚 Subject Registry")
    subject = st.selectbox("Select the field of study:", [
        "English: Tenses", "English: Grammar", "English: Pronunciation",
        "English: Vocabulary", "English: Conversation", 
        "English: Writing", "Medicine", "Law", "Engineering",
        "Business Management", "Arts & Humanities", "General Knowledge"
    ])
    st.session_state.current_subject = subject
    
    # --- SIDEBAR: THE DOCUMENT UPLOADER ---
with st.sidebar:
    st.header("📜 Academy Library")
    uploaded_file = st.file_uploader("Upload your Course Workbook (PDF)", type="pdf")

    if uploaded_file is not None:
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # This is the vital bridge!
            st.session_state.pdf_text = text
            st.success("Workbook safely filed in the archives!")
        except Exception as e:
            st.error(f"The Librarian is struggling: {e}")
    
    # Study Streak
    today = datetime.date.today()
    if st.session_state.last_visit_date != today:
        if st.session_state.last_visit_date == today - datetime.timedelta(days=1):
            st.session_state.streak_count += 1
        else:
            st.session_state.streak_count = 1
        st.session_state.last_visit_date = today
    st.markdown(f"🔥 **Study Streak:** {st.session_state.streak_count} Days")

    # Reference Library
    st.subheader("🏛️ Reference Library")
    with st.expander("🇬🇧 British Idioms"):
        st.write("* 'Chuffed to bits': Happy")
        st.write("* 'A spot of bother': A problem")
        st.write("* 'Taking the biscuit': Surprising")
    
    # Dictionary Tool
    with st.expander("📕 Quick Dictionary"):
        word_to_lookup = st.text_input("Look up a word:").strip()
        if word_to_lookup:
            try:
                resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_lookup}")
                if resp.status_code == 200:
                    st.write(f"**Def:** {resp.json()[0]['meanings'][0]['definitions'][0]['definition']}")
            except: st.error("Library Offline.")

    # London Weather
    try:
        weather_data = requests.get("https://wttr.in/London?format=%c+%t").text
        st.info(f"🇬🇧 London: {weather_data}")
    except: pass

    # WhatsApp Dean
    your_phone_number = "27833976517"
    encoded_msg = urllib.parse.quote("Hello Dean! I need assistance...")
    st.link_button("💬 WhatsApp Dean", f"https://wa.me/{your_phone_number}?text={encoded_msg}")
    
    if st.button("🧹 Reset Session"):
        st.session_state.clear()
        st.rerun()

    st.caption("© 2026 J Steenekamp | Sir Ryan's Academy")

# --- 6. PLACEMENT TEST ---
if st.session_state.english_level is None:
    st.title(f"🎓 Welcome, {st.session_state.student_name}!")
    with st.container(border=True):
        st.subheader("Placement Evaluation")
        path = st.radio("Proceed:", ["I know my level", "Test me!"], horizontal=True)
        if path == "I know my level":
            lvl = st.selectbox("Rank:", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Confirm"):
                st.session_state.english_level = lvl
                st.rerun()
        else:
            ans = st.text_input("If I ___ (be) you, I'd study. (Fill blank):")
            if st.button("Submit"):
                if "were" in ans.lower(): st.session_state.english_level = "Advanced"
                else: st.session_state.english_level = "Beginner"
                st.rerun()
    st.stop()

# --- 7. MAIN HUB ---
st.markdown("<h1 style='text-align: center; color: #002366;'>🎓 Sir Ryan’s Academy</h1>", unsafe_allow_html=True)
show_welcome_letter()

# --- 7.5 VOICE RECORDING STUDIO ---
st.write("---")
col_audio1, col_audio2 = st.columns(2)

with col_audio1:
    st.subheader("🎤 Oral Examination")
    st.write("Record your pronunciation or a message for Sir Ryan:")
    
    # The Recording Button
    audio_recording = mic_recorder(
        start_prompt="⏺️ Start Recording",
        stop_prompt="⏹️ Stop & Save",
        key="academy_mic"
    )

with col_audio2:
    if audio_recording:
        st.subheader("🎧 Review Recording")
        st.audio(audio_recording['bytes'])
        
        if st.button("📤 Submit for Grading", key="submit_voice_btn"):
            # Logic to add to gradebook
            st.session_state.gradebook.append({
                "Subject": st.session_state.current_subject,
                "Student": st.session_state.student_name,
                "Grade": "Oral Pending..."
            })
            st.success("Your voice note has been delivered to the Headmaster's study.")
            st.balloons()

# Quick Action Buttons
st.write("### ⚡ Quick Actions")
btn_col1, btn_col2, btn_col3 = st.columns(3)
with btn_col1:
    if st.button("📝 Start Quiz"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, give me a quick quiz!"})
        st.rerun()
with btn_col2:
    if st.button("📚 New Homework"):
        st.session_state.homework_task = "Write a paragraph using the word 'Quintessential'."
        st.rerun()
with btn_col3:
    if st.button("🏆 View Merits"):
        st.toast(f"You have {st.session_state.merits} merits!")

# Homework Hub
if st.session_state.homework_task:
    with st.expander("📝 Current Homework", expanded=True):
        st.info(f"**Task:** {st.session_state.homework_task}")
        hw_ans = st.text_area("Your Answer:")
        if st.button("Hand In"):
            st.session_state.homework_history.append({"task": st.session_state.homework_task, "answer": hw_ans})
            st.session_state.merits += 1
            st.session_state.homework_task = None
            st.balloons()
            st.rerun()

# --- ACADEMY DIAGNOSTIC PANEL ---
with st.expander("🔍 Academy System Status"):
    if "pdf_text" in st.session_state and st.session_state.pdf_text:
        st.success(f"✅ Document Loaded: {len(st.session_state.pdf_text)} characters detected.")
        if st.checkbox("Show extracted text preview"):
            st.write(st.session_state.pdf_text[:500] + "...")
    else:
        st.error("❌ No document detected in memory. Please upload your PDF in the sidebar.")

# --- 8. THE CLEAN ACADEMY CHAT HUB ---
st.write("---")

# 1. Prepare the context from your 7-Day Course PDF
full_context = st.session_state.get("pdf_text", "No document uploaded yet.")
short_context = full_context[:8000] # Kept lean to avoid the 413 error

# 2. THE CHAT INTERFACE
if prompt := st.chat_input("Ask Sir Ryan about your course..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sir Ryan is consulting the workbook..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Sir Ryan's Personality & Instructions
                system_instruction = f"""
                You are Sir Ryan, a posh British tutor. 
                Use the following course text to help the student: {short_context}
                Your goal: Help the student master the STAR method and professional etiquette.
                Always swap "cookies" for "biscuits" and use British spelling.
                """
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                )
                
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                speak_text(response)
                
            except Exception as e:
                st.error(f"The Library is a bit cluttered, Dean: {e}")

# Footer
st.write("---")
if st.button("🎓 Graduate"):
    st.session_state.graduated = True
    st.balloons()
