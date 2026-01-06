import streamlit as st
from groq import Groq
import PyPDF2
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time
import datetime
import random
import requests
import urllib.parse

# --- 1. PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Sir Ryan’s Academy", page_icon="🎓")

# Initialize all session states in one clean sweep
initial_states = {
    "authenticated": False,
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
    "last_visit_date": datetime.date.today()
}

for key, value in initial_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. VOICE FUNCTION ---
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

# --- 4. THE SECURITY GATE ---
if not st.session_state.authenticated:
    st.title("🛡️ The Academy Gate")
    license_key = st.text_input("Enter your License Key:", type="password")
    if st.button("Unlock the Study Hub"):
        if license_key == "Oxford2026":
            st.session_state.authenticated = True
            st.session_state.needs_intro = True
            st.rerun()
        else:
            st.error("I'm afraid that key doesn't fit the lock.")
    st.stop()

# --- 5. THE ACADEMY SIDEBAR (The Master Office) ---
with st.sidebar:
    st.title("🏫 Academy Office")

    # --- DAILY INSPIRATION ---
    st.write("---")
    st.subheader("💡 Today's Scholarly Thought")
    st.info("'The man who does not read has no advantage over the man who cannot read.' — Mark Twain")

    # Word of the Day Selection
    words_dict = {
        "Pulchritudinous": "Breath-taking, physically beautiful.",
        "Mellifluous": "Sweet or musical; pleasant to hear.",
        "Quintessential": "The most perfect example of a quality.",
        "Fastidious": "Very attentive to accuracy and detail.",
        "Sanguine": "Optimistic in a difficult situation."
    }
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    word_list = list(words_dict.keys())
    daily_word = word_list[day_of_year % len(word_list)]

    with st.expander("🇬🇧 Word of the Day"):
        st.info(f"**{daily_word}**")
        st.write(f"*{words_dict[daily_word]}*")

    # User Profile Info
    st.write("---")
    st.markdown(f"**Scholar:** {st.session_state.name}")
    st.markdown(f"**Level:** {st.session_state.english_level if st.session_state.english_level else 'Unassessed'}")
    
    # Study Streak
    today = datetime.date.today()
    if st.session_state.last_visit_date != today:
        if st.session_state.last_visit_date == today - datetime.timedelta(days=1):
            st.session_state.streak_count += 1
        else:
            st.session_state.streak_count = 1
        st.session_state.last_visit_date = today
    st.markdown(f"🔥 **Study Streak:** {st.session_state.streak_count} Days")

    st.write("---")

    # 1. THE REFERENCE LIBRARY
    st.subheader("🏛️ Reference Library")
    with st.expander("🇬🇧 British Idioms"):
        st.write("* 'Chuffed to bits': Happy")
        st.write("* 'A spot of bother': A problem")
        st.write("* 'Taking the biscuit': Particularly surprising/annoying")
    
    with st.expander("📜 Literature Links"):
        st.markdown("[🕵️ Sherlock Holmes](https://www.gutenberg.org/files/1661/1661-h/1661-h.htm)")
        st.markdown("[🐇 Alice in Wonderland](https://www.gutenberg.org/files/11/11-h/11-h.htm)")
        st.markdown("[Pride & Prejudice](https://www.gutenberg.org/ebooks/1342)")

    # 2. THE TOOLS (Dictionary & Progress)
    st.subheader("🛠️ Scholar Tools")
    
    with st.expander("📕 Quick Dictionary"):
        word_to_lookup = st.text_input("Look up a word:", key="dict_search_sidebar").strip()
        if word_to_lookup:
            try:
                resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_lookup}")
                if resp.status_code == 200:
                    data = resp.json()[0]
                    st.write(f"**Def:** {data['meanings'][0]['definitions'][0]['definition']}")
                else: st.warning("Word not found.")
            except: st.error("Library is closed (Offline).")

    # Progress Bar
    word_count = len(st.session_state.vocab_bank)
    goal = 10
    progress = min(word_count / goal, 1.0)
    st.caption(f"Vocabulary Progress: {word_count}/{goal}")
    st.progress(progress)

    # London Weather
    try:
        weather_data = requests.get("https://wttr.in/London?format=%c+%t").text
        st.info(f"🇬🇧 London: {weather_data}")
    except: st.caption("Weather vane stuck!")

    st.write("---")

    # 3. ADMINISTRATIVE & CONTACT
    your_phone_number = "27833976517"
    encoded_msg = urllib.parse.quote("Hello Dean! I need assistance...")
    st.link_button("💬 WhatsApp Dean", f"https://wa.me/{your_phone_number}?text={encoded_msg}")
    
    if st.button("🧹 Reset Academy Session", key="sidebar_final_reset"):
        st.session_state.clear()
        st.rerun()
    
    st.caption("© 2026 J Steenekamp")

# --- 6. PLACEMENT TEST (Gatekeeper) ---
if st.session_state.name != "Student" and st.session_state.english_level is None:
    st.title(f"🎓 Welcome, {st.session_state.name}!")
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
                elif "was" in ans.lower(): st.session_state.english_level = "Intermediate"
                else: st.session_state.english_level = "Beginner"
                st.rerun()
    st.stop()

# --- 7. GRADUATION VIEW ---
if st.session_state.graduated:
    st.balloons()
    cert_name = st.session_state.get("name", "Scholar")
    st.markdown(f'<div style="border: 5px solid #002366; padding: 20px; text-align: center;"><h1>Graduation Certificate</h1><p>Well done, {cert_name}!</p></div>', unsafe_allow_html=True)
    if st.button("Back to Study"):
        st.session_state.graduated = False
        st.rerun()
    st.stop()

# --- 8. MAIN CLASSROOM ---
st.markdown("<h1 style='text-align: center; color: #002366;'>🎓 Sir Ryan’s Academy</h1>", unsafe_allow_html=True)

# --- NEW: THE RESTORED QUICK ACTION BUTTONS ---
st.write("### ⚡ Quick Actions")
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("📝 Start Quiz", key="main_quiz_btn"):
        st.session_state.messages.append({"role": "user", "content": "Sir Ryan, please give me a quick 3-question quiz on British English!"})
        st.rerun()

with btn_col2:
    if st.button("📚 New Homework", key="main_hw_btn"):
        # This triggers the assignment logic
        st.session_state.homework_task = random.choice([
            "Explain 'Their' vs 'There'", 
            "Write a paragraph about London", 
            "Define 'Quintessential'"
        ])
        st.rerun()

with btn_col3:
    if st.button("🏆 View Merits", key="main_merit_btn"):
        st.toast(f"You have earned {st.session_state.merits} merits so far!")

st.write("---")

# Intro Greeting
if st.session_state.needs_intro:
    intro = f"Good morning! I am Sir Ryan. Welcome to the Academy, {st.session_state.name}. How shall we begin?"
    st.session_state.messages.append({"role": "assistant", "content": intro})
    speak_text(intro)
    st.session_state.needs_intro = False

    # --- 8.5 INSTRUCTION & PRIVACY BOXES ---
st.write("---")
with st.expander("📖 How to use the Academy"):
    st.markdown("""
    If the microphone is being a bit 'dodgy', follow these steps:
    1. **Type your question** in the chat box at the bottom.
    2. **Press Enter** on your keyboard.
    3. **Wait a tick** for Sir Ryan to consult his books.
    4. **Listen:** His voice will play automatically once the text appears.
    *Note: Ensure your speakers are on and you've clicked somewhere on the page to 'wake up' the audio!*
    """)

with st.expander("🛡️ Privacy & Security"):
    st.info("""
    **Your Privacy is Paramount:**
    * **Local Learning:** Your typed questions are processed by Ollama right here on your laptop.
    * **Voice Processing:** Only the text (not your voice) is briefly sent to the cloud to generate Sir Ryan's accent.
    * **Data:** We do not store your personal conversations outside of this session.
    """)

# Homework & Voice Tasks
col1, col2 = st.columns(2)

with col1:
    with st.expander("📝 Homework Hub", expanded=True): # Added 'expanded=True' so it's easy to see
        if st.button("Assign New Task", key="assign_hw_main"):
            st.session_state.homework_task = random.choice([
                "Explain 'Their' vs 'There'", 
                "Write a paragraph about London", 
                "Define the word 'Quintessential'"
            ])
        
        if st.session_state.homework_task:
            st.info(f"**Current Task:** {st.session_state.homework_task}")
            hw_ans = st.text_area("Write your answer here:", key="hw_input_area")
            if st.button("Hand In Homework", key="submit_hw_btn"):
                st.session_state.homework_history.append({
                    "task": st.session_state.homework_task, 
                    "answer": hw_ans
                })
                st.session_state.merits += 1
                st.session_state.homework_task = None
                st.balloons()
                st.rerun()
with col2:
    with st.expander("🎤 Recording Studio"):
        uploaded_audio = st.file_uploader("Upload Practice Audio", type=['mp3', 'wav'])
        if uploaded_audio: st.audio(uploaded_audio)

# --- 7. CHAT HUB (THE NEW CLOUD BRAIN) ---
if prompt := st.chat_input("Ask Sir Ryan anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # This tells the app to use the 'Golden Key' in your Secrets vault
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # We send the conversation to Groq instead of Ollama
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Sir Ryan, a posh British tutor."}] + st.session_state.messages,
        )
        
        response = completion.choices[0].message.content
        st.markdown(response)
        speak_text(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})

# Transcript & Graduation Button
st.write("---")
with st.expander("🎓 View Transcript"):
    for h in st.session_state.homework_history:
        st.write(f"**Task:** {h['task']}\n*Ans:* {h['answer']}")
if st.button("🎓 Graduate & Download Report"):
    st.session_state.graduated = True
    st.rerun()
