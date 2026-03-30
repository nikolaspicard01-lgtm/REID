import streamlit as st
import os
import tempfile
import time

from utils.downloader import download_reel_audio
from utils.transcriber import transcribe_audio
from utils.script_generator import extract_concept, generate_script

st.set_page_config(
    page_title="REID - Reel to Script",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .script-output {
        background-color: #1E1E2E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("REID")
st.subheader("Paste a Facebook Reel. Get a viral script.")

# API key in sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        help="Your Anthropic API key",
    )
    if api_key:
        st.session_state["api_key"] = api_key

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Paste a Facebook reel link")
    st.markdown("2. We download & transcribe it")
    st.markdown("3. AI extracts the core concept")
    st.markdown("4. AI writes a new original script")
    st.markdown("5. Copy your script & go")

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Main input
url = st.text_input(
    "Facebook Reel URL",
    placeholder="https://www.facebook.com/reel/...",
)

generate_btn = st.button("Generate Script", type="primary", use_container_width=True)

if generate_btn:
    if not api_key:
        st.error("Please enter your Claude API key in the sidebar.")
    elif not url:
        st.error("Please paste a Facebook reel URL.")
    else:
        progress = st.progress(0, text="Starting...")

        try:
            # Step 1: Download
            progress.progress(10, text="Downloading reel...")
            audio_path = download_reel_audio(url)
            progress.progress(30, text="Reel downloaded.")

            # Step 2: Transcribe
            progress.progress(40, text="Transcribing audio...")
            transcript = transcribe_audio(audio_path)
            progress.progress(60, text="Transcription complete.")

            # Clean up audio file
            try:
                os.remove(audio_path)
                os.rmdir(os.path.dirname(audio_path))
            except OSError:
                pass

            # Step 3: Extract concept
            progress.progress(70, text="Extracting concept...")
            concept = extract_concept(transcript, api_key)
            progress.progress(80, text="Concept extracted.")

            # Step 4: Generate script
            progress.progress(85, text="Writing your script...")
            script = generate_script(concept, api_key)
            progress.progress(100, text="Done!")

            # Store results
            result = {
                "url": url,
                "transcript": transcript,
                "concept": concept,
                "script": script,
                "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state["history"].insert(0, result)

            time.sleep(0.5)
            progress.empty()

            # Display results
            st.success("Script generated!")

            tab1, tab2, tab3 = st.tabs(["Script", "Concept", "Transcript"])

            with tab1:
                st.markdown(script)
                st.download_button(
                    "Download Script",
                    script,
                    file_name="reid_script.md",
                    mime="text/markdown",
                )

            with tab2:
                st.markdown(concept)

            with tab3:
                st.text_area("Original Transcript", transcript, height=200)

        except Exception as e:
            progress.empty()
            st.error(f"Something went wrong: {str(e)}")

# Show history
if st.session_state["history"]:
    st.divider()
    st.subheader("Previous Generations")
    for i, item in enumerate(st.session_state["history"]):
        with st.expander(f"{item['timestamp']} — {item['url'][:60]}..."):
            tab1, tab2 = st.tabs(["Script", "Concept"])
            with tab1:
                st.markdown(item["script"])
            with tab2:
                st.markdown(item["concept"])
