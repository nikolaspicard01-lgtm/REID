import streamlit as st
import os
import time

from utils.downloader import download_reel_audio
from utils.transcriber import transcribe_audio
from utils.script_generator import extract_concept, generate_script, revise_script
from utils.pdf_export import parse_script_to_pdf
from utils.profile_scraper import scrape_profile_reels, format_duration, format_views

st.set_page_config(
    page_title="ABXStudio - Reel to Script",
    page_icon="ABX",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS — ABXStudio black/white/grey brand
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background: #0a0a0a;
    }

    /* Header */
    .reid-header {
        text-align: center;
        padding: 3rem 0 0.5rem 0;
    }
    .reid-logo {
        font-family: 'Inter', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 0.25em;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
    }
    .reid-logo span {
        background: linear-gradient(180deg, #ffffff 0%, #666666 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .reid-tagline {
        font-family: 'Inter', sans-serif;
        color: #666666;
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }
    .reid-divider {
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffffff, transparent);
        margin: 1.5rem auto;
    }

    /* Steps */
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
        color: #444444;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        transition: color 0.3s;
    }
    .step.active { color: #ffffff; }
    .step.done { color: #888888; }
    .step-num {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1.5px solid currentColor;
    }

    /* Script output */
    .script-container {
        background: #111111;
        border: 1px solid #222222;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        line-height: 1.8;
        color: #cccccc;
    }

    /* Reel cards */
    .reel-card {
        background: #111111;
        border: 1px solid #222222;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.2s;
    }
    .reel-card:hover {
        border-color: #ffffff;
        background: #161616;
    }
    .reel-title {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #e0e0e0;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }
    .reel-meta {
        font-family: 'Inter', sans-serif;
        color: #666666;
        font-size: 0.8rem;
    }
    .reel-meta span {
        margin-right: 1.2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        justify-content: center;
        background: #111111;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 24px;
        border: none;
        color: #666666;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #000000 !important;
        border: none;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: #ffffff;
        color: #000000;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: #e0e0e0;
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
    }

    /* Secondary / other buttons */
    .stButton > button:not([kind="primary"]) {
        background: #161616;
        color: #cccccc;
        border: 1px solid #333333;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #222222;
        border-color: #ffffff;
        color: #ffffff;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #cccccc;
        transition: all 0.2s;
    }
    .stDownloadButton > button:hover {
        background: #1a1a1a;
        border-color: #ffffff;
        color: #ffffff;
    }

    /* Text input */
    .stTextInput > div > div > input {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #e0e0e0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #ffffff;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15);
    }
    .stTextInput > div > div > input::placeholder {
        color: #555555;
    }

    /* Text area */
    .stTextArea > div > div > textarea {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #ffffff;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #444444 0%, #ffffff 100%);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #111111;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #ffffff !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    .stSidebar {
        background: #0d0d0d;
        border-right: 1px solid #1a1a1a;
    }
    .stSidebar .stMarkdown {
        color: #999999;
    }

    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #333333, transparent);
        margin: 2.5rem 0;
    }

    .mode-description {
        color: #666666;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Section headers */
    h3, .stMarkdown h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    /* Labels */
    .stTextInput > label, .stTextArea > label {
        font-family: 'Inter', sans-serif;
        color: #888888;
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    /* Success/Error/Warning */
    .stAlert {
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="reid-header">
        <div class="reid-logo"><span>ABXStudio</span></div>
        <div class="reid-divider"></div>
        <div class="reid-tagline">Reel to Script in One Click</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        help="Your Anthropic API key",
    )
    if api_key:
        st.session_state["api_key"] = api_key

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        """
        **Browse Mode:** Paste a Facebook profile — we find their top reels for you to pick from.\n
        **Direct Mode:** Paste a single reel link to generate a script instantly.\n
        **Revise:** Not happy? Tell the AI what to change.
        """
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#555555'>Scripts are in standard screenplay format, ready for actors and production.</small>",
        unsafe_allow_html=True,
    )

# Session state
if "history" not in st.session_state:
    st.session_state["history"] = []


def run_pipeline(reel_url: str):
    """Run the full reel-to-script pipeline. Stores results in session state."""
    status = st.empty()
    progress = st.progress(0)

    try:
        # Step 1: Download
        status.markdown(
            '<div class="steps-container">'
            '<div class="step active"><div class="step-num">1</div> Downloading</div>'
            '<div class="step"><div class="step-num">2</div> Transcribing</div>'
            '<div class="step"><div class="step-num">3</div> Analyzing</div>'
            '<div class="step"><div class="step-num">4</div> Writing</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        progress.progress(10)
        audio_path = download_reel_audio(reel_url)
        progress.progress(25)

        # Step 2: Transcribe
        status.markdown(
            '<div class="steps-container">'
            '<div class="step done"><div class="step-num">✓</div> Downloaded</div>'
            '<div class="step active"><div class="step-num">2</div> Transcribing</div>'
            '<div class="step"><div class="step-num">3</div> Analyzing</div>'
            '<div class="step"><div class="step-num">4</div> Writing</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        transcript = transcribe_audio(audio_path)
        progress.progress(50)

        try:
            os.remove(audio_path)
            os.rmdir(os.path.dirname(audio_path))
        except OSError:
            pass

        # Step 3: Extract concept
        status.markdown(
            '<div class="steps-container">'
            '<div class="step done"><div class="step-num">✓</div> Downloaded</div>'
            '<div class="step done"><div class="step-num">✓</div> Transcribed</div>'
            '<div class="step active"><div class="step-num">3</div> Analyzing</div>'
            '<div class="step"><div class="step-num">4</div> Writing</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        concept = extract_concept(transcript, api_key)
        progress.progress(70)

        # Step 4: Generate script
        status.markdown(
            '<div class="steps-container">'
            '<div class="step done"><div class="step-num">✓</div> Downloaded</div>'
            '<div class="step done"><div class="step-num">✓</div> Transcribed</div>'
            '<div class="step done"><div class="step-num">✓</div> Analyzed</div>'
            '<div class="step active"><div class="step-num">4</div> Writing Script</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        script = generate_script(concept, api_key)
        progress.progress(100)

        # Done
        status.markdown(
            '<div class="steps-container">'
            '<div class="step done"><div class="step-num">✓</div> Downloaded</div>'
            '<div class="step done"><div class="step-num">✓</div> Transcribed</div>'
            '<div class="step done"><div class="step-num">✓</div> Analyzed</div>'
            '<div class="step done"><div class="step-num">✓</div> Complete</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        pdf_bytes = parse_script_to_pdf(script)

        st.session_state["current_script"] = script
        st.session_state["current_concept"] = concept
        st.session_state["current_transcript"] = transcript
        st.session_state["current_pdf"] = pdf_bytes
        st.session_state["revision_count"] = 0

        result = {
            "url": reel_url,
            "transcript": transcript,
            "concept": concept,
            "script": script,
            "pdf": pdf_bytes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        }
        st.session_state["history"].insert(0, result)

        time.sleep(0.8)
        progress.empty()
        return True

    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"Something went wrong: {str(e)}")
        return False


# ── Mode Selection ──
mode_browse, mode_direct = st.tabs(["Browse Profile", "Direct Link"])

# ── Browse Profile Mode ──
with mode_browse:
    st.markdown(
        '<div class="mode-description">Paste a Facebook profile or page URL. We\'ll find their reels so you can pick the best ones.</div>',
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        profile_url = st.text_input(
            "Facebook Profile URL",
            placeholder="https://www.facebook.com/pagename",
            key="profile_input",
        )
        scan_btn = st.button(
            "Scan Reels", type="primary", use_container_width=True
        )

    if scan_btn and profile_url:
        if not api_key:
            st.error("Enter your Claude API key in the sidebar.")
        else:
            with st.spinner("Scanning profile for reels... this may take a moment."):
                reels = scrape_profile_reels(profile_url)
                if reels:
                    st.session_state["scraped_reels"] = reels
                    st.session_state["profile_source"] = profile_url
                else:
                    st.warning(
                        "Could not find reels from this profile. Facebook may be blocking access. "
                        "Try using the **Direct Link** tab instead."
                    )

    if "scraped_reels" in st.session_state and st.session_state["scraped_reels"]:
        reels = st.session_state["scraped_reels"]
        st.markdown(f"**Found {len(reels)} reels** — sorted by views (best first)")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        for idx, reel in enumerate(reels):
            col_info, col_action = st.columns([4, 1])

            with col_info:
                title = reel["title"][:80] if reel["title"] else "Untitled Reel"
                views = format_views(reel["view_count"])
                likes = format_views(reel["like_count"])
                dur = format_duration(reel["duration"])

                st.markdown(
                    f"""<div class="reel-card">
                        <div class="reel-title">{idx + 1}. {title}</div>
                        <div class="reel-meta">
                            <span>Views: {views}</span>
                            <span>Likes: {likes}</span>
                            <span>Duration: {dur}</span>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with col_action:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Script it", key=f"reel_{idx}", use_container_width=True):
                    run_pipeline(reel["url"])

# ── Direct Link Mode ──
with mode_direct:
    st.markdown(
        '<div class="mode-description">Paste a single Facebook reel link to generate a script instantly.</div>',
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        url = st.text_input(
            "Facebook Reel URL",
            placeholder="https://www.facebook.com/reel/...",
            label_visibility="collapsed",
            key="direct_input",
        )
        generate_btn = st.button(
            "Generate Script", type="primary", use_container_width=True
        )

    if generate_btn:
        if not api_key:
            st.error("Enter your Claude API key in the sidebar.")
        elif not url:
            st.error("Paste a Facebook reel URL above.")
        else:
            run_pipeline(url)


# ── Display Current Script ──
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
                file_name="abxstudio_screenplay.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with dl_col2:
            st.download_button(
                "Download Script (.txt)",
                script,
                file_name="abxstudio_screenplay.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with dl_col3:
            st.download_button(
                "Download Markdown",
                script,
                file_name="abxstudio_screenplay.md",
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
        "<span style='color:#666666'>Not happy with something? Tell the AI what to change.</span>",
        unsafe_allow_html=True,
    )

    revision_count = st.session_state.get("revision_count", 0)

    feedback = st.text_area(
        "What would you like to change?",
        placeholder="e.g. Make the twist more dramatic, change the setting to a hospital, make the antagonist more subtle...",
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

                if st.session_state["history"]:
                    st.session_state["history"][0]["script"] = revised
                    st.session_state["history"][0]["pdf"] = revised_pdf

                st.rerun()
            except Exception as e:
                st.error(f"Revision failed: {str(e)}")
    elif revise_btn and not feedback:
        st.warning("Type your feedback above before clicking Revise.")

# ── History ──
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
                        file_name=f"abxstudio_script_{i}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{i}",
                        use_container_width=True,
                    )
                with col2:
                    st.download_button(
                        "Download .txt",
                        item["script"],
                        file_name=f"abxstudio_script_{i}.txt",
                        mime="text/plain",
                        key=f"txt_{i}",
                        use_container_width=True,
                    )
            with h_tab2:
                st.markdown(item["concept"])
