import streamlit as st

# 1. Basic Title
st.title("🏛️ Sir Ryan's Academy: Testing Phase")

# 2. Check for the other files
try:
    import styles
    st.success("✅ styles.py found!")
except Exception as e:
    st.error(f"❌ styles.py missing or error: {e}")

try:
    import academy_data
    st.success("✅ academy_data.py found!")
    st.write(f"Subjects loaded: {len(academy_data.SUBJECTS)}")
except Exception as e:
    st.error(f"❌ academy_data.py missing or error: {e}")

# 3. Check for Secrets
if "GROQ_API_KEY" in st.secrets:
    st.success("✅ Groq API Key found in secrets!")
else:
    st.warning("⚠️ Groq API Key NOT found. Check your .streamlit/secrets.toml file.")

st.write("If you can see this, the Academy foundations are solid, Dean!")
