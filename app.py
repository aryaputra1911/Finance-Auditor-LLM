import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import streamlit as st
import re
from datetime import datetime
from src.bridge_llama import SovereignLlamaBridge, DEFAULT_CONFIG
from src.agent_system import FinbenchSystem

# UI configuraton
st.set_page_config(
    page_title="Finance Auditor LLM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# config design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Menggunakan variabel tema Streamlit agar adaptif */
    .stApp {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    
    .block-container {
        max-width: 850px !important;
        width: 850px !important;
        margin: auto !important;
        padding-top: 2rem !important;
        padding-bottom: 16rem !important;
    }

    /* Styling Chat Messages */
    .stChatMessage {
        padding: 1.5rem 0 !important;
        background-color: transparent !important;
        border-bottom: 1px solid var(--secondary-background-color) !important;
    }
    
    /* Assistant Message khusus */
    div[data-testid="stChatMessageAssistant"] {
        border-left: 3px solid #1a73e8 !important;
        padding-left: 25px !important;
        /* Warna latar belakang yang lembut untuk dark/light mode */
        background-color: rgba(128, 128, 128, 0.05) !important;
    }

    /* Fixed Chat Input agar tidak "tembus pandang" di dark mode */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 90px !important;
        left: 0 !important;
        right: 0 !important;
        margin: auto !important;
        width: 90% !important;
        max-width: 800px !important;
        z-index: 1000 !important;
        background-color: var(--background-color) !important;
        border: 1px solid var(--secondary-background-color) !important;
        border-radius: 28px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stChatInput"] textarea {
        max-height: 150px !important;
        overflow-y: auto !important;
    }
    /* Footer adaptif */
    .main-footer-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        /* Efek gradien mengikuti warna background tema */
        background: linear-gradient(to top, var(--background-color) 80%, rgba(0,0,0,0));
        z-index: 998;
        padding: 20px 0 15px 0;
        pointer-events: none;
    }
    
    .footer-content {
        pointer-events: auto;
        text-align: center;
    }

    /* Landing Header adaptif */
    .landing-header-text {
        color: #1a73e8 !important;
    }
    
    .landing-subtext {
        color: var(--text-color) !important;
        opacity: 0.8;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid var(--secondary-background-color) !important;
    }
    .active-audit-header {
        position: sticky; 
        top: 0; 
        background-color: var(--secondary-background-color) !important; 
        backdrop-filter: blur(10px); 
        z-index: 99; 
        text-align: center; 
        padding: 15px; 
        border-bottom: 1px solid var(--secondary-background-color);
        border-radius: 8px; /* Opsional: agar lebih estetik */
    }

    .active-audit-header span {
        color: var(--primary-color) !important;
        font-weight: 600;
        letter-spacing: 1.5px;
    }
    div[data-testid="stChatMessage"] div.stMarkdown {
        width: 100% !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        word-break: break-word !important;
    }
    
    /* Mencegah teks berdempetan secara horizontal */
    div[data-testid="stChatMessage"] p {
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
    }
    """, unsafe_allow_html=True)

# system intialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource
def init_core():
    # Architectural design focused on epistemic integrity
    engine = FinbenchSystem(
        canonical_path=DEFAULT_CONFIG["CANONICAL_PATH"],
        tavily_api_key=DEFAULT_CONFIG["TAVILY_API_KEY"]
    )
    return SovereignLlamaBridge(engine)

bridge = init_core()

def clean_output(text):
    def replace_headers(match):
        return f"### {match.group(1).replace('_', ' ').title()}"
    return re.sub(r'\[([A-Z_]+)\]', replace_headers, text)

# sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #1a73e8; margin-bottom: 0;'>Finance Auditor AI</h2>", unsafe_allow_html=True)
    st.caption("Structural System")
    
    st.markdown("---")
    
    with st.expander("🗺️ USER GUIDANCE", expanded=False):
        st.markdown("""
        * **Identify**: Input a ticker or company name.
        * **Audit**: Focus on structural logic, not price predictions.
        * **Analyze**: Use the 'Ugly Scenario' to stress-test your thesis.
        """)
    
    with st.expander("📊 EVIDENCE HIERARCHY", expanded=False):
        st.markdown("""
            To maintain structural integrity, our audit processes data through an epistemic filter:
        * **Tier 1:** Forensic Financials (Cash Flow, Debt, Margins) - PRIMARY EVIDENCE.
        * **Tier 2:** Business Archetypes (Moats, Network Effects, IP) - STRUCTURAL PROOF.
        * **Tier 3:** Macro Context (Regulation, Demographics) - **CONTEXTUAL SIGNAL.
        * **Tier 4:** Institutional Research (Analyst Opinions, White Papers) - SECONDARY NOISE.
        * **Tier 5:** Market Psychology (Price Surges, Viral Tweets, Expert Consensus) - REJECTED AS NOISE.

        *Note: We prioritize Tier 1 & 2 data because they represent verifiable structural reality. Tiers 3, 4, and 5 are excluded from the core audit as they often contain speculative bias, market noise, and transient sentiment that can distort objective financial truth.*""")

    with st.expander("​✨​ SYSTEM ADVANTAGES", expanded=True):
        st.markdown("""
        1. **Epistemic Integrity**
        2. **Anti-Hype Guardrails**
        3. **Contextual Ratios**
        4. **Falsifiability**
        """)

    st.markdown("---")
    if st.button("New Audit Session", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

landing_placeholder = st.empty()

if st.session_state.chat_history:
    landing_placeholder.empty()
    st.markdown("""
        <div class="active-audit-header">
            <span>AUDITOR FINANCE LLM</span>
        </div>
    """, unsafe_allow_html=True)
else:
    with landing_placeholder.container():
        st.markdown("""
        <div class="landing-container" style="
            position: fixed; 
            top: 23vh; 
            left: 58%; 
            transform: translateX(-50%); 
            text-align: left; 
            width: 800px; 
            z-index: 0;
        ">
            <h1 style="font-size: 3.2rem; font-weight: 600; letter-spacing: -1px; color: #1a73e8; margin-bottom: 5px;">
                Audit your Financial Thesis.
            </h1>
            <p style="font-size: 1.2rem; color: #5f6368; margin-left: 90px; max-width: 600px;">
                Stripping market noise to reveal structural truth.
            </p>
        </div>
        <style>
            div[data-testid="stChatInput"] { 
                bottom: 44vh !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                position: fixed !important;
                width: 90% !important;
                max-width: 800px !important;
            }
        </style>
        """, unsafe_allow_html=True)

# Main Chat Container
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(clean_output(msg["content"]))
            
            if msg["role"] == "assistant":
                msg_sources = msg.get("sources", [])
                if msg_sources:
                    with st.expander("📚 Audit Sources & Evidence", expanded=False):
                        for src in msg_sources:
                            if src.startswith("http"):
                                st.markdown(f"○ [{src}]({src})")
                            else:
                                st.markdown(f"○ {src}")
# footer
st.markdown("""
    <div class="main-footer-container">
        <div class="footer-content">
            <p style="color: #d32f2f; font-size: 0.8rem; margin: 0; font-weight: 500;">
                 Warning: System can make mistake, please check the response again.
            </p>
            <p style="color: #9e9e9e; font-size: 0.7rem; margin-top: 4px;">
                Made by Muhammad Arya Putra Handrian | Student @ Universitas Diponegoro
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# input and interaction
query = st.chat_input("Enter ticker or question...")

if query:
    landing_placeholder.empty() 
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_history])
                    result = bridge.smart_query(history_str)

                    if isinstance(result, dict):
                        answer = result.get("answer", "")
                        # Ambil sources, tapi langsung kosongkan jika terdeteksi error limit
                        error_keywords = ["token has reached", "Rate Limit", "PRECISION LOCK"]
                        is_rate_limited = any(word.upper() in answer.upper() for word in error_keywords)
                        
                        sources = [] if is_rate_limited else result.get("sources", [])
                    else:
                        answer = result
                        sources = []

                    st.markdown(clean_output(answer))
                    
                    if sources: 
                        with st.expander("📚 Audit Sources & Evidence", expanded=True):
                            for src in sources:
                                st.markdown(f"○ {src}")

                    # Simpan ke history (Data yang disimpan sudah bersih dari sources jika error)
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    st.error(f"Audit Session Error: {str(e)}")