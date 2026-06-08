import io
import streamlit as st
from agent import run_investment_agent
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI

# Initialize OpenAI Client for Whisper
openai_client = OpenAI()

# 1. Page Configuration
st.set_page_config(
    page_title="Airport Investment Agent", 
    layout="wide", 
    page_icon="🛫",
    initial_sidebar_state="collapsed"
)

# 2. Initialize Session State Variables (Preventing racing conditions)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_healthy" not in st.session_state:
    st.session_state.api_healthy = True
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# 3. Premium CSS Injection (Gradient text, absolute avatar removal, pulse animation & Tech Background)
st.markdown("""
    <style>
    /* PREMIUM TECH BACKGROUND: Mesh Gradient + Blueprint Tech Grid */
    [data-testid="stAppViewContainer"] {
        background-color: #0b0f19 !important;
        background-image:
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.07) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(192, 132, 252, 0.07) 0px, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.006) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.006) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 35px 35px, 35px 35px !important;
    }
    
    /* Ensure the sidebar matches the dark industrial palette */
    [data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Modern Metallic Gradient for Title */
    .centered-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .centered-caption {
        text-align: center;
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    
    /* Global Artifact Removal */
    .stDeployButton {display: none !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* Absolute Avatar Removal */
    div[data-testid="stChatMessage"] > div:first-child:not([data-testid="stChatMessageContent"]) {
        display: none !important;
        width: 0px !important;
    }
    [data-testid="stChatMessageAvatar"] {
        display: none !important;
        width: 0px !important;
    }
    div[data-testid="stChatMessageContent"] {
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    
    /* Real-time Status Pulse Animation */
    .pulse-container {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #0f172a;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse 1.6s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    /* Bloomberg Table Style */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 20px 0 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    th {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        padding: 12px 14px !important;
        border: 1px solid #334155 !important;
    }
    td {
        padding: 10px 14px !important;
        border: 1px solid #334155 !important;
        background-color: #0f172a !important;
    }
    tr:nth-child(even) td { background-color: #1e293b !important; }
    h3 { color: #38bdf8 !important; margin-top: 25px !important; border-bottom: 1px solid #334155; padding-bottom: 8px; }
    
    /* 🛠️ PREMIUM MIC & COLUMN ALIGNMENT FOR GEMINI LOOK */
    
    /* ניקוי מוחלט של קופסת המיקרופון והתאמת גודל קומפקטית */
    div[data-testid="element-container"]:has(iframe) {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: auto !important;
    }
    div[data-testid="element-container"] iframe {
        border-radius: 50% !important;
        height: 40px !important;
        width: 40px !important;
        margin-left: 12px !important;  /* הזזה קלה ימינה לתוך שולי הבר */
        padding-top: 2px !important;   /* איזון אנכי מדויק */
    }
    
    /* הפיכת הבלוק המשותף לקפסולת פרימיום ממורכזת בתחתית */
    div[data-testid="stHorizontalBlock"] {
        position: fixed !important;
        bottom: 24px !important;
        max-width: 840px !important;   /* רוחב זהה לחלוטין לבר של Gemini */
        width: 100% !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        background: #111827 !important; /* צבע רקע כהה ונקי המתמזג עם תיבת הטקסט */
        padding: 6px 12px !important;
        border-radius: 35px !important; /* קצוות עגולים לחלוטין */
        border: 1px solid #1e293b !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important; /* יישור אנכי מושלם של המיקרופון והטקסט */
    }

    /* העלמת שכבות הרקע והגבולות המקוריות של תיבת הטקסט של סטרימליט */
    div[data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 100% !important;
    }
    div[data-testid="stChatInput"] fieldset {
        border: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Render Centered Corporate Header
st.markdown('<div class="centered-title">Airport Investment Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="centered-caption">Identify and analyze US airport modernization & expansion opportunities.</div>', unsafe_allow_html=True)
st.markdown("---")

# 5. SIDEBAR: WORKSPACE CONFIGURATION
with st.sidebar:
    st.title("Workspace Configuration")
    st.markdown("**Role & Purpose:**\nThis panel manages global environment parameters and active database connection states.")
    st.markdown("---")
    
    st.subheader("Session Management")
    st.markdown("Clear memory to purge old variables when switching your investment focus to a completely new region.")
    if st.button("Clear Conversation & Context", use_container_width=True):
        st.session_state.messages = []
        st.session_state.api_healthy = True  # Hard reset back to healthy state
        st.session_state.last_processed_audio = None
        st.rerun()
        
    st.markdown("---")
    st.subheader("Operational Pipeline Status")
    
    if st.session_state.api_healthy:
        st.markdown(
            '<div class="pulse-container"><div class="pulse-dot"></div>'
            '<span style="color: #64748b; font-size: 13px;">AirLabs Live API Grid Synchronized</span></div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="pulse-container"><div class="pulse-dot" style="background-color: #ef4444; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);"></div>'
            '<span style="color: #ef4444; font-size: 13px; font-weight: 600;">AirLabs API Offline - Fallback Active</span></div>', 
            unsafe_allow_html=True
        )

# 6. Display Active Chat History
st.markdown('<div style="margin-bottom: 100px;">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message.get("role") in ["user", "assistant"] and message.get("content"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 7. Unified Input Pipeline (Voice + Text Inside a Single Premium Pill Bar)
user_query = None

# יצירת שורה משותפת ממורכזת: המיקרופון משמאל ותיבת הטקסט מימין
input_col1, input_col2 = st.columns([1, 14])  # הגדלנו מעט את יחס העמודה של הטקסט למראה מאוזן יותר

with input_col1:
    audio_box = mic_recorder(
        start_prompt="🎤",
        stop_prompt="🛑",
        key="voice_chat",
        just_once=True
    )

with input_col2:
    chat_query = st.chat_input("Ask me about airport investments...")
    if chat_query:
        user_query = chat_query

# Intercept and process incoming binary audio array streams
if audio_box and 'bytes' in audio_box:
    audio_bytes = audio_box['bytes']
    
    if st.session_state.last_processed_audio != audio_bytes:
        st.session_state.last_processed_audio = audio_bytes
        
        with st.spinner("🎧 Transcribing voice prompt via OpenAI Whisper..."):
            try:
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.wav"
                
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                
                if transcript.text.strip():
                    user_query = transcript.text
            except Exception as e:
                st.error(f"Voice Transcription Pipeline Interrupted: {str(e)}")

# 8. Execution and Agent Runtime Core Loop
if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing aviation data and infrastructure models..."):
            response_text, updated_history = run_investment_agent(user_query, chat_history=st.session_state.messages)
            st.markdown(response_text)
            
    # Synchronize persistent session state history
    st.session_state.messages = updated_history
    st.rerun()