import streamlit as st
import os
import time

from utils.downloader import download_reel_audio
from utils.transcriber import transcribe_audio
from utils.script_generator import extract_concept, generate_script, revise_script
from utils.pdf_export import parse_script_to_pdf
from utils.profile_scraper import scrape_profile_reels, format_duration, format_views

st.set_page_config(
    page_title="ABXStudio",
    page_icon="ABX",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp { background: #000000; }

    /* ── Welcome / API Key Screen ── */
    .welcome {
        text-align: center;
        max-width: 480px;
        margin: 8vh auto 0 auto;
    }
    .welcome-logo {
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 0.3em;
        background: linear-gradient(180deg, #fff 0%, #555 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .welcome-sub {
        color: #555;
        font-size: 0.95rem;
        font-weight: 300;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }
    .welcome-label {
        color: #666;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        text-align: left;
        margin-bottom: 0.5rem;
    }

    /* ── Top bar ── */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.2rem 0;
        border-bottom: 1px solid #1a1a1a;
        margin-bottom: 2rem;
    }
    .topbar-logo {
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: 0.2em;
        color: #fff;
    }
    .topbar-mode {
        color: #555;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ── Mode selector cards ── */
    .mode-grid {
        display: flex;
        gap: 1.5rem;
        max-width: 700px;
        margin: 0 auto 2rem auto;
    }
    .mode-card {
        flex: 1;
        background: #0a0a0a;
        border: 1px solid #222;
        border-radius: 14px;
        padding: 2rem 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .mode-card:hover {
        border-color: #fff;
        background: #111;
    }
    .mode-icon {
        font-size: 2rem;
        margin-bottom: 0.8rem;
    }
    .mode-title {
        color: #fff;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .mode-desc {
        color: #555;
        font-size: 0.82rem;
        font-weight: 400;
        line-height: 1.5;
    }

    /* ── Section header ── */
    .section-header {
        color: #fff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .section-sub {
        color: #555;
        font-size: 0.85rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }

    /* ── Reel cards ── */
    .reel-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        transition: all 0.15s;
    }
    .reel-card:hover {
        border-color: #444;
        background: #0f0f0f;
    }
    .reel-rank {
        color: #333;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .reel-title {
        color: #ddd;
        font-size: 0.92rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
        line-height: 1.4;
    }
    .reel-stats {
        color: #444;
        font-size: 0.78rem;
        font-weight: 400;
    }
    .reel-stats span { margin-right: 1rem; }

    /* ── Script output ── */
    .script-box {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        line-height: 1.9;
        color: #bbb;
    }

    /* ── Progress steps ── */
    .psteps {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
    }
    .pstep {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #333;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .pstep.on { color: #fff; }
    .pstep.ok { color: #666; }
    .pstep-dot {
        width: 24px; height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        border: 1.5px solid currentColor;
    }

    /* ── Divider ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #222, transparent);
        margin: 2.5rem 0;
    }

    /* ── Streamlit overrides ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; justify-content: center;
        background: #0a0a0a; border-radius: 10px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 8px; padding: 8px 24px;
        border: none; color: #555; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #fff !important; color: #000 !important;
    }

    .stButton > button[kind="primary"] {
        background: #fff; color: #000; border: none;
        border-radius: 10px; padding: 0.7rem 2rem;
        font-weight: 600; font-size: 0.9rem;
        letter-spacing: 0.06em; text-transform: uppercase;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: #ddd; transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(255,255,255,0.08);
    }

    .stButton > button:not([kind="primary"]) {
        background: #0a0a0a; color: #aaa;
        border: 1px solid #333; border-radius: 8px;
        font-weight: 500; transition: all 0.2s;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #151515; border-color: #fff; color: #fff;
    }

    .stDownloadButton > button {
        background: #0a0a0a; border: 1px solid #222;
        border-radius: 8px; color: #aaa; font-weight: 500;
        transition: all 0.2s;
    }
    .stDownloadButton > button:hover {
        border-color: #fff; color: #fff; background: #111;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #0a0a0a; border: 1px solid #222;
        border-radius: 10px; padding: 0.8rem 1rem;
        font-size: 0.95rem; color: #ddd;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #fff;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.1);
    }
    .stTextInput > div > div > input::placeholder { color: #444; }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #333, #fff);
    }

    .stCheckbox label span { color: #ccc !important; }

    .streamlit-expanderHeader {
        background: #0a0a0a; border-radius: 8px;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .stSidebar { background: #050505; border-right: 1px solid #111; }

    h3 { color: #fff; font-weight: 600; letter-spacing: 0.02em; }

    .stTextInput > label, .stTextArea > label {
        color: #666; font-weight: 500; letter-spacing: 0.02em;
    }

    .stAlert { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
if "history" not in st.session_state:
    st.session_state["history"] = []
if "view" not in st.session_state:
    st.session_state["view"] = "welcome"  # welcome | choose | paste | scan | results | script


# ══════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════
def run_pipeline(reel_url: str):
    api_key = st.session_state.get("api_key", "")
    status = st.empty()
    progress = st.progress(0)

    try:
        def show_step(step):
            labels = ["Downloading", "Transcribing", "Analyzing", "Writing"]
            html = '<div class="psteps">'
            for i, label in enumerate(labels):
                if i < step:
                    cls = "ok"
                    num = "✓"
                elif i == step:
                    cls = "on"
                    num = str(i + 1)
                else:
                    cls = ""
                    num = str(i + 1)
                html += f'<div class="pstep {cls}"><div class="pstep-dot">{num}</div> {label}</div>'
            html += "</div>"
            status.markdown(html, unsafe_allow_html=True)

        show_step(0)
        progress.progress(10)
        audio_path = download_reel_audio(reel_url)
        progress.progress(25)

        show_step(1)
        transcript = transcribe_audio(audio_path)
        progress.progress(50)

        try:
            os.remove(audio_path)
            os.rmdir(os.path.dirname(audio_path))
        except OSError:
            pass

        show_step(2)
        concept = extract_concept(transcript, api_key)
        progress.progress(70)

        show_step(3)
        script = generate_script(concept, api_key)
        progress.progress(100)

        show_step(4)

        pdf_bytes = parse_script_to_pdf(script)

        st.session_state["current_script"] = script
        st.session_state["current_concept"] = concept
        st.session_state["current_transcript"] = transcript
        st.session_state["current_pdf"] = pdf_bytes
        st.session_state["revision_count"] = 0
        st.session_state["view"] = "script"

        st.session_state["history"].insert(0, {
            "url": reel_url,
            "transcript": transcript,
            "concept": concept,
            "script": script,
            "pdf": pdf_bytes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        })

        time.sleep(0.5)
        progress.empty()
        status.empty()
        st.rerun()

    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"Something went wrong: {str(e)}")


# ══════════════════════════════════════════════
# VIEW: WELCOME — API Key Entry
# ══════════════════════════════════════════════
if st.session_state["view"] == "welcome":
    st.markdown(
        """
        <div class="welcome">
            <div class="welcome-logo">ABXSTUDIO</div>
            <div class="welcome-sub">Reel to Script Engine</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown('<div class="welcome-label">Enter your API key to start</div>', unsafe_allow_html=True)
        key_input = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-...",
            label_visibility="collapsed",
        )
        if st.button("Start", type="primary", use_container_width=True):
            if key_input:
                st.session_state["api_key"] = key_input
                st.session_state["view"] = "choose"
                st.rerun()
            else:
                st.error("Please enter your Claude API key.")


# ══════════════════════════════════════════════
# VIEW: CHOOSE MODE
# ══════════════════════════════════════════════
elif st.session_state["view"] == "choose":
    # Top bar
    st.markdown(
        '<div class="topbar">'
        '<div class="topbar-logo">ABXSTUDIO</div>'
        '<div class="topbar-mode">Choose Mode</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align:center; margin-bottom: 2rem;">
            <div class="section-header">What would you like to do?</div>
            <div class="section-sub">Choose how you want to find your next script</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_a, col_b, col_r = st.columns([1, 2, 2, 1])

    with col_a:
        st.markdown(
            """
            <div class="mode-card">
                <div class="mode-icon">&#9654;</div>
                <div class="mode-title">Paste a Reel</div>
                <div class="mode-desc">Got a specific reel? Paste the link and we'll create a new script from it.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Paste a Reel", type="primary", use_container_width=True, key="btn_paste"):
            st.session_state["view"] = "paste"
            st.rerun()

    with col_b:
        st.markdown(
            """
            <div class="mode-card">
                <div class="mode-icon">&#128269;</div>
                <div class="mode-desc">Scan Facebook profiles for the best performing reels, then pick your favorites.</div>
                <div class="mode-title">Scan Profiles</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Scan Profiles", type="primary", use_container_width=True, key="btn_scan"):
            st.session_state["view"] = "scan"
            st.rerun()


# ══════════════════════════════════════════════
# VIEW: PASTE A REEL
# ══════════════════════════════════════════════
elif st.session_state["view"] == "paste":
    st.markdown(
        '<div class="topbar">'
        '<div class="topbar-logo">ABXSTUDIO</div>'
        '<div class="topbar-mode">Paste a Reel</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("< Back", key="back_paste"):
        st.session_state["view"] = "choose"
        st.rerun()

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="section-header">Paste your Facebook reel link</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">We\'ll transcribe it and create a brand new script based on the same concept.</div>', unsafe_allow_html=True)

        url = st.text_input(
            "Reel URL",
            placeholder="https://www.facebook.com/reel/...",
            label_visibility="collapsed",
        )
        if st.button("Generate Script", type="primary", use_container_width=True):
            if url:
                run_pipeline(url)
            else:
                st.error("Paste a reel URL above.")


# ══════════════════════════════════════════════
# VIEW: SCAN PROFILES
# ══════════════════════════════════════════════
elif st.session_state["view"] == "scan":
    st.markdown(
        '<div class="topbar">'
        '<div class="topbar-logo">ABXSTUDIO</div>'
        '<div class="topbar-mode">Scan Profiles</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("< Back", key="back_scan"):
        st.session_state["view"] = "choose"
        st.rerun()

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="section-header">Facebook profiles to scan</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Add the profiles you want to monitor. We\'ll find their best reels.</div>', unsafe_allow_html=True)

        # Default profiles
        if "scan_profiles" not in st.session_state:
            st.session_state["scan_profiles"] = [
                "https://www.facebook.com/dramatizeme",
                "https://www.facebook.com/dharmannofficial",
            ]

        # Show current profiles
        profiles = st.session_state["scan_profiles"]
        for i, p in enumerate(profiles):
            col_url, col_del = st.columns([5, 1])
            with col_url:
                st.markdown(
                    f'<div class="reel-card"><div class="reel-title">{p}</div></div>',
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("Remove", key=f"rm_prof_{i}"):
                    st.session_state["scan_profiles"].pop(i)
                    st.rerun()

        # Add new profile
        new_prof = st.text_input(
            "Add profile URL",
            placeholder="https://www.facebook.com/pagename",
            key="new_profile_url",
        )
        if st.button("Add Profile", use_container_width=True):
            if new_prof:
                st.session_state["scan_profiles"].append(new_prof.strip())
                st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.button("Scan All Profiles", type="primary", use_container_width=True):
            all_reels = []
            scan_msg = st.empty()

            for i, profile_url in enumerate(st.session_state["scan_profiles"]):
                scan_msg.markdown(
                    f'<div class="section-sub">Scanning profile {i + 1} of {len(st.session_state["scan_profiles"])}...</div>',
                    unsafe_allow_html=True,
                )
                try:
                    reels = scrape_profile_reels(profile_url)
                    for r in reels:
                        r["source"] = profile_url.rstrip("/").split("/")[-1]
                    all_reels.extend(reels)
                except Exception as e:
                    st.warning(f"Could not scan {profile_url}: {e}")

            scan_msg.empty()

            if all_reels:
                all_reels.sort(key=lambda x: x["view_count"], reverse=True)
                st.session_state["discovered_reels"] = all_reels
                st.session_state["view"] = "results"
                st.rerun()
            else:
                st.error("No reels found. Facebook may be blocking access.")


# ══════════════════════════════════════════════
# VIEW: SCAN RESULTS — Pick reels
# ══════════════════════════════════════════════
elif st.session_state["view"] == "results":
    st.markdown(
        '<div class="topbar">'
        '<div class="topbar-logo">ABXSTUDIO</div>'
        '<div class="topbar-mode">Select Reels</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("< Back to Profiles", key="back_results"):
        st.session_state["view"] = "scan"
        st.rerun()

    reels = st.session_state.get("discovered_reels", [])

    st.markdown(f'<div class="section-header">Found {len(reels)} reels</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Select the ones you want to turn into scripts, then hit Generate.</div>', unsafe_allow_html=True)

    # Select all / clear
    col_sa, col_cl, col_sp = st.columns([1, 1, 4])
    with col_sa:
        if st.button("Select All", use_container_width=True):
            for i in range(len(reels)):
                st.session_state[f"pick_{i}"] = True
            st.rerun()
    with col_cl:
        if st.button("Clear All", use_container_width=True):
            for i in range(len(reels)):
                st.session_state[f"pick_{i}"] = False
            st.rerun()

    # Reel list
    for idx, reel in enumerate(reels):
        col_check, col_info = st.columns([0.4, 5])

        title = (reel["title"][:70] + "...") if reel["title"] and len(reel["title"]) > 70 else (reel["title"] or "Untitled")
        views = format_views(reel["view_count"])
        likes = format_views(reel["like_count"])
        dur = format_duration(reel["duration"])
        source = reel.get("source", "")

        with col_check:
            st.checkbox("s", key=f"pick_{idx}", label_visibility="collapsed")

        with col_info:
            st.markdown(
                f"""<div class="reel-card">
                    <div class="reel-rank">#{idx + 1} &middot; {source}</div>
                    <div class="reel-title">{title}</div>
                    <div class="reel-stats">
                        <span>{views} views</span>
                        <span>{likes} likes</span>
                        <span>{dur}</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Generate button
    selected = [i for i in range(len(reels)) if st.session_state.get(f"pick_{i}", False)]
    count = len(selected)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if st.button(
            f"Generate {count} Script{'s' if count != 1 else ''}" if count > 0 else "Select reels above",
            type="primary",
            use_container_width=True,
            disabled=count == 0,
        ):
            for i, idx in enumerate(selected):
                reel = reels[idx]
                st.markdown(f'<div class="section-sub">Generating script {i + 1} of {count}...</div>', unsafe_allow_html=True)
                run_pipeline(reel["url"])


# ══════════════════════════════════════════════
# VIEW: SCRIPT OUTPUT
# ══════════════════════════════════════════════
elif st.session_state["view"] == "script":
    st.markdown(
        '<div class="topbar">'
        '<div class="topbar-logo">ABXSTUDIO</div>'
        '<div class="topbar-mode">Your Script</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    col_back, col_new = st.columns([1, 1])
    with col_back:
        if st.button("< New Script", key="back_script"):
            st.session_state["view"] = "choose"
            # Clean up current script state
            for key in ["current_script", "current_concept", "current_transcript", "current_pdf"]:
                st.session_state.pop(key, None)
            st.rerun()

    script = st.session_state["current_script"]
    pdf_bytes = st.session_state["current_pdf"]

    # Tabs: Script / Concept / Transcript
    tab_script, tab_concept, tab_transcript = st.tabs(
        ["Screenplay", "Concept Analysis", "Original Transcript"]
    )

    with tab_script:
        st.markdown(f'<div class="script-box">{script}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "Download PDF",
                pdf_bytes,
                file_name="abxstudio_screenplay.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "Download .txt",
                script,
                file_name="abxstudio_screenplay.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col3:
            st.download_button(
                "Download .md",
                script,
                file_name="abxstudio_screenplay.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab_concept:
        st.markdown(st.session_state.get("current_concept", ""))

    with tab_transcript:
        st.text_area(
            "transcript",
            st.session_state.get("current_transcript", ""),
            height=250,
            label_visibility="collapsed",
        )

    # ── Revise ──
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Revise Script</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Not happy with something? Tell the AI what to change.</div>', unsafe_allow_html=True)

    revision_count = st.session_state.get("revision_count", 0)
    api_key = st.session_state.get("api_key", "")

    feedback = st.text_area(
        "feedback",
        placeholder="e.g. Make the twist bigger, change setting to a hospital, add more tension in the middle...",
        height=100,
        label_visibility="collapsed",
        key=f"rev_{revision_count}",
    )

    if st.button("Revise Script", type="primary", use_container_width=True, key="revise_btn"):
        if feedback:
            with st.spinner("Revising..."):
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
        else:
            st.warning("Type your feedback above.")


# ══════════════════════════════════════════════
# HISTORY (shown on script view and choose view)
# ══════════════════════════════════════════════
if st.session_state["view"] in ("choose", "script") and st.session_state["history"]:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### Previous Scripts")

    for i, item in enumerate(st.session_state["history"]):
        with st.expander(f"{item['timestamp']} — {item['url'][:50]}..."):
            h_tab1, h_tab2 = st.tabs(["Screenplay", "Concept"])
            with h_tab1:
                st.markdown(item["script"])
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        "PDF", item["pdf"],
                        file_name=f"abx_script_{i}.pdf",
                        mime="application/pdf",
                        key=f"hpdf_{i}",
                        use_container_width=True,
                    )
                with c2:
                    st.download_button(
                        ".txt", item["script"],
                        file_name=f"abx_script_{i}.txt",
                        mime="text/plain",
                        key=f"htxt_{i}",
                        use_container_width=True,
                    )
            with h_tab2:
                st.markdown(item["concept"])
