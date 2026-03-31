import streamlit as st
import os
import time

from utils.downloader import download_reel_audio
from utils.transcriber import transcribe_audio
from utils.script_generator import extract_concept, generate_script, revise_script
from utils.pdf_export import parse_script_to_pdf

st.set_page_config(
    page_title="REID - Reel to Script",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a polished look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Header */
    .reid-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .reid-logo {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.15em;
        margin-bottom: 0.2rem;
    }
    .reid-tagline {
        font-family: 'Inter', sans-serif;
        color: #8892b0;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 0.05em;
    }

    /* Input card */
    .input-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem auto;
        max-width: 700px;
        backdrop-filter: blur(10px);
    }

    /* Steps indicator */
    .steps-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #4a5568;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        transition: color 0.3s;
    }
    .step.active {
        color: #667eea;
    }
    .step.done {
        color: #48bb78;
    }
    .step-num {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.8rem;
        border: 2px solid currentColor;
    }

    /* Script output */
    .script-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        line-height: 1.8;
    }

    /* Result tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 8px 24px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: transparent;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.03em;
        transition: all 0.3s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s;
    }
    .stDownloadButton > button:hover {
        background: rgba(255,255,255,0.1);
        border-color: #667eea;
    }

    /* Text input */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #e2e8f0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    .stSidebar {
        background: rgba(10, 10, 15, 0.95);
    }

    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
        margin: 2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="reid-header">
        <div class="reid-logo">REID</div>
        <div class="reid-tagline">Reel to Script in One Click</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar — API key + info
with st.sidebar:
    st.markdown("### Settings")
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        help="Your Anthropic API key — never stored, only used in your session",
    )
    if api_key:
        st.session_state["api_key"] = api_key

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        """
        **1.** Paste a Facebook reel link\n
        **2.** Audio is extracted & transcribed\n
        **3.** AI analyzes the core concept\n
        **4.** A new screenplay is generated\n
        **5.** Download as PDF
        """
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#4a5568'>Scripts are in standard screenplay format, ready for actors and production.</small>",
        unsafe_allow_html=True,
    )

# Session state
if "history" not in st.session_state:
    st.session_state["history"] = []

# Main input area
col_spacer_l, col_main, col_spacer_r = st.columns([1, 3, 1])

with col_main:
    url = st.text_input(
        "Facebook Reel URL",
        placeholder="https://www.facebook.com/reel/...",
        label_visibility="collapsed",
    )

    generate_btn = st.button(
        "Generate Script", type="primary", use_container_width=True
    )

# Processing
if generate_btn:
    if not api_key:
        st.error("Enter your Claude API key in the sidebar (click **>** top-left).")
    elif not url:
        st.error("Paste a Facebook reel URL above.")
    else:
        # Step indicators
        status = st.empty()
        progress = st.progress(0)

        try:
            # Step 1
            status.markdown(
                """
                <div class="steps-container">
                    <div class="step active"><div class="step-num">1</div> Downloading</div>
                    <div class="step"><div class="step-num">2</div> Transcribing</div>
                    <div class="step"><div class="step-num">3</div> Analyzing</div>
                    <div class="step"><div class="step-num">4</div> Writing</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            progress.progress(10)
            audio_path = download_reel_audio(url)
            progress.progress(25)

            # Step 2
            status.markdown(
                """
                <div class="steps-container">
                    <div class="step done"><div class="step-num">✓</div> Downloaded</div>
                    <div class="step active"><div class="step-num">2</div> Transcribing</div>
                    <div class="step"><div class="step-num">3</div> Analyzing</div>
                    <div class="step"><div class="step-num">4</div> Writing</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            transcript = transcribe_audio(audio_path)
            progress.progress(50)

            try:
                os.remove(audio_path)
                os.rmdir(os.path.dirname(audio_path))
            except OSError:
                pass

            # Step 3
            status.markdown(
                """
                <div class="steps-container">
                    <div class="step done"><div class="step-num">✓</div> Downloaded</div>
                    <div class="step done"><div class="step-num">✓</div> Transcribed</div>
                    <div class="step active"><div class="step-num">3</div> Analyzing</div>
                    <div class="step"><div class="step-num">4</div> Writing</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            concept = extract_concept(transcript, api_key)
            progress.progress(70)

            # Step 4
            status.markdown(
                """
                <div class="steps-container">
                    <div class="step done"><div class="step-num">✓</div> Downloaded</div>
                    <div class="step done"><div class="step-num">✓</div> Transcribed</div>
                    <div class="step done"><div class="step-num">✓</div> Analyzed</div>
                    <div class="step active"><div class="step-num">4</div> Writing Script</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            script = generate_script(concept, api_key)
            progress.progress(100)

            # Done
            status.markdown(
                """
                <div class="steps-container">
                    <div class="step done"><div class="step-num">✓</div> Downloaded</div>
                    <div class="step done"><div class="step-num">✓</div> Transcribed</div>
                    <div class="step done"><div class="step-num">✓</div> Analyzed</div>
                    <div class="step done"><div class="step-num">✓</div> Complete</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Generate PDF
            pdf_bytes = parse_script_to_pdf(script)

            # Store in session state for revision
            st.session_state["current_script"] = script
            st.session_state["current_concept"] = concept
            st.session_state["current_transcript"] = transcript
            st.session_state["current_pdf"] = pdf_bytes
            st.session_state["revision_count"] = 0

            # Store in history
            result = {
                "url": url,
                "transcript": transcript,
                "concept": concept,
                "script": script,
                "pdf": pdf_bytes,
                "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state["history"].insert(0, result)

            time.sleep(0.8)
            progress.empty()

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"Something went wrong: {str(e)}")

# Display current script (persists across reruns for revision)
if "current_script" in st.session_state:
    script = st.session_state["current_script"]
    pdf_bytes = st.session_state["current_pdf"]

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    tab_script, tab_concept, tab_transcript = st.tabs(
        ["Screenplay", "Concept Analysis", "Original Transcript"]
    )

    with tab_script:
        st.markdown(
            f'<div class="script-container">{script}</div>',
            unsafe_allow_html=True,
        )

        dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 1])
        with dl_col1:
            st.download_button(
                "Download PDF",
                pdf_bytes,
                file_name="reid_screenplay.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with dl_col2:
            st.download_button(
                "Download Script (.txt)",
                script,
                file_name="reid_screenplay.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with dl_col3:
            st.download_button(
                "Download Markdown",
                script,
                file_name="reid_screenplay.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab_concept:
        st.markdown(st.session_state.get("current_concept", ""))

    with tab_transcript:
        st.text_area(
            "Original Transcript",
            st.session_state.get("current_transcript", ""),
            height=250,
            label_visibility="collapsed",
        )

    # Revision section
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Revise Script")
    st.markdown(
        "<span style='color:#8892b0'>Not happy with something? Tell the AI what to change.</span>",
        unsafe_allow_html=True,
    )

    revision_count = st.session_state.get("revision_count", 0)

    feedback = st.text_area(
        "What would you like to change?",
        placeholder="e.g. Make the twist more dramatic, change the setting to a hospital, make the antagonist more subtle, add more tension in the middle...",
        height=100,
        key=f"revision_input_{revision_count}",
    )

    revise_btn = st.button("Revise Script", type="primary", use_container_width=True)

    if revise_btn and feedback:
        with st.spinner("Revising your script..."):
            try:
                revised = revise_script(script, feedback, api_key)
                revised_pdf = parse_script_to_pdf(revised)

                st.session_state["current_script"] = revised
                st.session_state["current_pdf"] = revised_pdf
                st.session_state["revision_count"] = revision_count + 1

                # Update the most recent history entry
                if st.session_state["history"]:
                    st.session_state["history"][0]["script"] = revised
                    st.session_state["history"][0]["pdf"] = revised_pdf

                st.rerun()
            except Exception as e:
                st.error(f"Revision failed: {str(e)}")
    elif revise_btn and not feedback:
        st.warning("Type your feedback above before clicking Revise.")

# History section
if st.session_state["history"]:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Previous Scripts")

    for i, item in enumerate(st.session_state["history"]):
        with st.expander(f"**{item['timestamp']}** — {item['url'][:50]}..."):
            h_tab1, h_tab2 = st.tabs(["Screenplay", "Concept"])
            with h_tab1:
                st.markdown(item["script"])
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download PDF",
                        item["pdf"],
                        file_name=f"reid_script_{i}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{i}",
                        use_container_width=True,
                    )
                with col2:
                    st.download_button(
                        "Download .txt",
                        item["script"],
                        file_name=f"reid_script_{i}.txt",
                        mime="text/plain",
                        key=f"txt_{i}",
                        use_container_width=True,
                    )
            with h_tab2:
                st.markdown(item["concept"])
