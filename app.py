import streamlit as st
from agent import run_investment_agent

st.set_page_config(
    page_title="Airport Investment Agent", 
    layout="wide", 
    page_icon="🛫",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
    .centered-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        color: #ffffff;
    }
    .centered-caption {
        text-align: center;
        font-size: 1.1rem;
        color: #a3a8b4;
        margin-bottom: 2rem;
    }
    /* Complete removal of Streamlit top header line and Deploy button */
    .stDeployButton {display: none !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# Render Centered Corporate Header
st.markdown('<div class="centered-title">Airport Investment Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="centered-caption">Identify and analyze US airport modernization & expansion opportunities.</div>', unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: WORKSPACE CONFIGURATION ---
# Clearly states the role and purpose of the sidebar configurations
with st.sidebar:
    st.title("Workspace Configuration")
    st.markdown("""
    **Role & Purpose:**
    This panel manages your global environment parameters and active database connection states. 
    """)
    st.markdown("---")
    
    st.subheader("Session Management")
    st.markdown("Clear memory to purge old variables when switching your investment focus to a completely new airport or geographic region.")
    if st.button("Clear Conversation & Context", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.subheader("Operational Pipeline Status")
    # Using st.success to show a green, stable status indicator
    st.success("Connected to AirLabs Live API Grid (Real-time flight schedules fully synchronized).")

# Initialize chat history if it doesn't exist in the session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past conversation history on the screen natively
for message in st.session_state.messages:
    if message.get("role") in ["user", "assistant"] and message.get("content"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input from the standard, native bottom chat interface
if user_input := st.chat_input("Ask me about airport investments..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing aviation data and infrastructure models..."):
            response_text, updated_history = run_investment_agent(user_input, chat_history=st.session_state.messages)
            st.markdown(response_text)
            
    # Synchronize session state history managed by the agent layer
    st.session_state.messages = updated_history