import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import edge_tts
import asyncio
import base64
import time

# --- 1. FOUNDATION ---
st.set_page_config(page_title="Sir Ryan's Academy", page_icon="👑", layout="wide")

# --- 2. LOGO ---
col_logo, _ = st.columns([1, 2])
with col_logo:
    try:
        st.image("logo.png", width=350)
    except:
        st.markdown("""
            <div style="background-color: #002147; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; text-align: center;">
                <h1 style="color: #C5A059; margin: 0;">🏛️</h1>
                <h2 style="color: #C5A059; margin: 0; letter-spacing: 2px;">SIR RYAN'S ACADEMY</h2>
                <p style="color: #C5A059; font-style: italic;">Snassy English Excellence</p>
            </div>
        """, unsafe_allow_html=True)

# --- 3. SESSION STATES ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "messages": [], "student_name": "Scholar",
        "nickname": "Scholar", "avatar": None, "mute": False,
        "english_level": "Pending", "current_subject": "General English",
        "progress": {"Grammar": 0, "Tenses": 0, "Vocab": 0, "Business": 0}
    })

# --- 4. GATEKEEPER ---
if not st.session_state.authenticated:
    st.title("🏛️ Academy Registry")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("Full Name:")
        nick_in = st.text_input("Nickname:")
        u_photo = st.file_uploader("Upload Portrait:", type=['png', 'jpg', 'jpeg'])
    with c2:
        key_in = st.text_input("License Key:", type="password")
        if st.button("Register & Enter Academy"):
            if name_in and key_in.lower().strip() == "oxford2026":
                st.session_state.authenticated = True
                st.session_state.student_name = name_in
                st.session_state.nickname = nick_in if nick_in else name_in
                st.session_state.avatar = u_photo
                st.rerun()
    st.stop()

# --- 5. LEVEL TEST (RESTORED) ---
if st.session_state.english_level == "Pending":
    st.title("📜 Entrance Examination")
    if st.button("🏆 Returning Scholar (Skip)"):
        st.session_state.english_level = "Advanced Executive"
        st.rerun()
    with st.form("initial_test"):
        st.write("Determine your rank with these 10 questions...")
        # Placeholder for your 10 initial questions
        if st.form_submit_button("Submit Exam"):
            st.session_state.english_level = "Intermediate"
            st.rerun()
    st.stop()

# --- 6. VOICE ENGINE ---
def speak_text(text):
    if st.session_state.mute: return
    try:
        clean = text.replace("**", "").replace("#", "")
        communicate = edge_tts.Communicate(clean, "en-GB-RyanNeural")
        asyncio.run(communicate.save("temp.mp3"))
        with open("temp.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- 7. SIDEBAR (WITH RETAKE BUTTON) ---
with st.sidebar:
    if st.session_state.avatar: 
        st.image(st.session_state.avatar, width=150)
    st.markdown(f"### 👤 {st.session_state.nickname}")
    st.info(f"🏅 Level: {st.session_state.english_level}")
    st.session_state.mute = st.checkbox("🔇 Mute Sir Ryan")
    
    st.divider()
    # NEW: The Retake Button
    if st.button("🔄 Retake Level Test"):
        st.session_state.english_level = "Pending"
        st.rerun()
    
    st.divider()
    subjects = ["General English", "Tenses", "Grammar Mastery", "Pronunciation", "Vocabulary", "Writing Emails", "Writing Letters", "Writing Reports", "Business English", "Legal English", "Maths", "Arts & Culture", "ELS Prep", "Interview Prep", "🏆 GRAND FINAL (100 Qs)"]
    st.session_state.current_subject = st.selectbox("Current Focus Area:", subjects)

   import pdfplumber  # Ensure you add this to your requirements.txt

# --- 4.5 NEW: VAULT STORAGE LOGIC ---
if "vault" not in st.session_state:
    st.session_state.vault = {}  # Stores filename: text_content

# --- 7. SIDEBAR (REBUILT FOR THE VAULT) ---
with st.sidebar:
    # ... (Keep existing avatar/name/level code) ...

    st.divider()
    st.markdown("### 🏛️ Scholar's Personal Vault")
    if st.session_state.vault:
        for filename in st.session_state.vault.keys():
            st.write(f"📄 {filename}")
    else:
        st.caption("Your vault is currently empty, Scholar.")

    # ... (Keep existing Subject Selection and Library Links) ...

# --- 10. THE STUDY DESKS (PDF UPLOAD & ANALYSIS) ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    # ... (Keep existing Oral Practice code) ...

with col_right:
    st.subheader("📝 The Homework & Research Desk")
    hw_file = st.file_uploader("Upload Workbook or PDF to Vault:", type=['pdf'])
    
    if hw_file:
        if st.button("📤 Process & Save to Vault"):
            with st.spinner("Sir Ryan is reviewing the parchment..."):
                with pdfplumber.open(hw_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()
                
                # Save to session state vault
                st.session_state.vault[hw_file.name] = text
                st.success(f"'{hw_file.name}' has been safely stored in your Vault!")
                st.balloons()

    st.divider()
    if st.session_state.vault:
        selected_doc = st.selectbox("Select a file for Sir Ryan to read:", list(st.session_state.vault.keys()))
        doc_query = st.text_input(f"What shall Sir Ryan check in '{selected_doc}'?")
        
        if st.button("🧐 Analyse Document"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            context = st.session_state.vault[selected_doc][:4000] # First 4000 chars for context
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are Sir Ryan. You are reviewing a student's uploaded workbook. Answer their question based on the document text provided."},
                    {"role": "user", "content": f"Document Content: {context}\n\nStudent Question: {doc_query}"}
                ]
            ).choices[0].message.content
            
            st.info(response)
            speak_text(response)

    st.divider()
    st.link_button("💬 WhatsApp Dean", "https://wa.me/27833976517")
    
    if st.button("🚪 Save & Log Out"):
        st.session_state.authenticated = False
        st.session_state.english_level = "Pending"
        st.rerun()

# --- 8. MAIN HUB ---
st.title(f"Good day, {st.session_state.nickname}!")

# Progress Metrics
cols = st.columns(4)
for i, (subj, val) in enumerate(st.session_state.progress.items()):
    cols[i].metric(subj, f"{val}%")
    cols[i].progress(val/100)

# --- 9. THE MASTERY WING (QUIZZES) ---
st.divider()
st.subheader(f"📝 {st.session_state.current_subject} Mastery Quiz")

# This section handles both 20-question subject quizzes and the 100-question final
with st.expander(f"Click to start the {st.session_state.current_subject} Examination"):
    num_questions = 100 if "GRAND FINAL" in st.session_state.current_subject else 20
    with st.form("subject_quiz"):
        st.write(f"This assessment contains {num_questions} questions on {st.session_state.current_subject}.")
        # To keep the code clean, we use a loop for placeholders
        for i in range(1, num_questions + 1):
            st.radio(f"Question {i}: Select the most formal option.", ["Option A", "Option B", "Option C"], key=f"q{i}")
        
        if st.form_submit_button("Submit Examination"):
            st.balloons()
            st.success(f"Splendid! Your results for {st.session_state.current_subject} have been recorded. Have a biscuit!")

with col_left:
    st.subheader("🎤 Oral Examination & Elocution")
    audio_data = mic_recorder(
        start_prompt="⏺️ Begin Speaking",
        stop_prompt="⏹️ End & Submit to Sir Ryan",
        key='oral_recorder'
    )

    if audio_data:
        # 1. Play back for the scholar
        st.audio(audio_data['bytes'])
        
        if st.button("👂 Sir Ryan, did you hear that?"):
            with st.spinner("The Headmaster is listening intently..."):
                try:
                    # 2. Send the audio bytes to Groq's Whisper model
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # We save the bytes to a temporary file for the API
                    with open("temp_audio.wav", "wb") as f:
                        f.write(audio_data['bytes'])
                    
                    with open("temp_audio.wav", "rb") as audio_file:
                        transcription = client.audio.transcriptions.create(
                            file=("temp_audio.wav", audio_file.read()),
                            model="whisper-large-v3",
                            response_format="text"
                        )
                    
                    # 3. Sir Ryan gives feedback on the transcription
                    st.markdown(f"**Sir Ryan heard:** *\"{transcription}\"*")
                    
                    critique_prompt = f"The student said: '{transcription}'. Please critique their English, elocution, and grammar in a posh British way. Mention their {st.session_state.english_level} level and give them a biscuit if they did well."
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": "You are Sir Ryan. You just heard the student speak. Respond with a critique of their spoken English."},
                                  {"role": "user", "content": critique_prompt}]
                    ).choices[0].message.content
                    
                    st.info(response)
                    speak_text(response)
                    
                except Exception as e:
                    st.error("Sir Ryan's ear trumpet is a bit dusty. Please try again!")

# --- 11. CHAT HUB & COPYRIGHT (REPAIRED) ---
st.divider()
st.subheader("💬 Audience with the Headmaster")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Sir Ryan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": f"You are Sir Ryan, the formal British Headmaster. Student level: {st.session_state.english_level}. Mention biscuits. Use British spelling like colour and honour."}] + st.session_state.messages
            ).choices[0].message.content
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            speak_text(resp)
        except Exception as e:
            st.error("Sir Ryan is currently at tea. Please try again shortly.")

st.markdown("<br><hr><center><p style='color: #888888;'>© 2026 J Steenekamp | Sir Ryan's Academy | All Rights Reserved</p></center>", unsafe_allow_html=True)
