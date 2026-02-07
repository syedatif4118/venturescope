"""
VentureScope Streamlit App - AI-Powered VC Deal Flow Intelligence.
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# Project setup
# --------------------------------------------------

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.orchestrator import VentureScopeOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="VentureScope - AI Deal Flow Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 1rem;
}
.subheader {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}
.score-card {
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}
.recommendation-invest {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.recommendation-consider {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
}
.recommendation-pass {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
}
.metric-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Session State
# --------------------------------------------------


def init_session_state():
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None


def get_orchestrator():
    if st.session_state.orchestrator is None:
        try:
            st.session_state.orchestrator = VentureScopeOrchestrator()
        except Exception as e:
            st.error(f"Error initializing VentureScope: {str(e)}")
            st.stop()
    return st.session_state.orchestrator


# --------------------------------------------------
# UI Components
# --------------------------------------------------


def display_header():
    st.markdown(
        '<h1 class="main-header">🎯 VentureScope</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subheader">AI-Powered VC Deal Flow Intelligence Platform</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")


def display_sidebar():
    with st.sidebar:
        st.markdown("### 🚀 About")
        st.markdown(
            """
VentureScope uses autonomous AI agents to analyze startup pitch decks and generate 
comprehensive investment memos in minutes.

**Multi-Agent Pipeline:**
- 📄 Document Ingestion
- 📊 Market Analysis
- 👥 Team Assessment
- 💰 Financial Modeling
- ⚠️ Risk Flagging
- 📝 Memo Generation
"""
        )

        st.markdown("---")
        st.markdown("### ⚙️ Configuration")

        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if api_key:
            st.success("✅ HuggingFace API Connected")
        else:
            st.error("❌ API Key Missing")
            st.info("Add HUGGINGFACE_API_KEY to .env file")

        st.info("🤖 Model: Llama 3.1 70B")

        st.markdown("---")
        st.markdown("### 👤 Built by")
        st.markdown("**Syed Atif**")
        st.markdown("AI/ML Engineer | LLM Specialist")


def upload_pitch_deck():
    st.markdown("### 📤 Upload Pitch Deck")

    uploaded_file = st.file_uploader(
        "Choose a PDF pitch deck",
        type=["pdf"],
    )

    if uploaded_file:
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(
            f"✅ Uploaded: {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.1f} KB)"
        )

        return str(temp_path)

    return None


# --------------------------------------------------
# Main App
# --------------------------------------------------


def main():
    init_session_state()
    display_header()
    display_sidebar()

    pitch_deck_path = upload_pitch_deck()

    if pitch_deck_path:
        if st.button(
            "🚀 Analyze Pitch Deck",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Running AI analysis..."):
                orchestrator = get_orchestrator()

                try:
                    result = orchestrator.analyze_pitch_deck(
                        pitch_deck_path
                    )
                    st.session_state.analysis_result = result
                    st.success("✅ Analysis complete!")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    logger.error(str(e), exc_info=True)

    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        st.markdown("---")
        st.metric("Investment Score", f"{result['final_score']}/100")
        st.markdown("### 📝 Investment Memo")
        st.markdown(result["memo"])
    else:
        st.info("👆 Upload a pitch deck to get started!")


if __name__ == "__main__":
    main()
