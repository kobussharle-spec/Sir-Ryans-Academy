import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    .stApp { background: #fdfaf5; }
    /* The Gold & Navy Button */
    .stButton>button {
        background: linear-gradient(145deg, #002147, #003366);
        color: #C5A059;
        border: 2px solid #C5A059;
        border-radius: 20px;
        font-weight: bold;
        transition: 0.5s;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background: #C5A059;
        color: #002147;
        box-shadow: 0px 0px 20px #C5A059;
    }
    /* Snazzy Sidebar */
    [data-testid="stSidebar"] {
        background-color: #002147;
        border-right: 3px solid #C5A059;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    .box { 
        background: white; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #C5A059;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
