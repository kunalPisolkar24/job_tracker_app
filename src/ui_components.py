import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 5% 5% 5% 10%;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_error(msg: str):
    st.error(msg, icon="🚨")

def display_success(msg: str):
    st.success(msg, icon="✅")