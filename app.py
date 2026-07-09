# ============================================================
# Rambler 3.0 — Streamlit Demo Application
# Team Omnix | AMD Hackathon Track 2
# Powered by Gemma on AMD ROCm
# ============================================================

import streamlit as st
import tempfile
import json
import base64
import os
import time
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pipeline
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Rambler 3.0 — AI Video Captioning | Team Omnix",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (Premium Dark Theme) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* Global overrides */
.stApp {
    background: #06060e;
    font-family: 'Inter', sans-serif;
}

/* Header section */
.hero-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}

.hero-header::after {
    content: '';
    display: block;
    margin: 1.5rem auto 0;
    width: 60%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(237,28,36,0.4), rgba(255,107,53,0.3), rgba(237,28,36,0.4), transparent);
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ed1c24 0%, #ff6b35 50%, #ffab40 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.04em;
    margin-bottom: 0.3rem;
    line-height: 1.1;
}

.hero-subtitle {
    color: #7a7a95;
    font-size: 0.9rem;
    font-weight: 400;
    margin-bottom: 0.2rem;
}

.hero-team {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #44445a;
    font-family: 'JetBrains Mono', monospace;
    padding: 0.3rem 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 999px;
    background: rgba(255,255,255,0.02);
    margin-top: 0.5rem;
}

.hero-team strong {
    color: #ed1c24;
    font-weight: 700;
}

/* Cards */
.metric-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.25rem;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}

.metric-card h4 {
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

.metric-card p {
    font-size: 0.88rem;
    line-height: 1.7;
    color: #b0b0c8;
}

/* Style-specific colors */
.style-formal { color: #448aff !important; }
.style-sarcastic { color: #b388ff !important; }
.style-tech { color: #00e676 !important; }
.style-fun { color: #ff6b35 !important; }

.style-border-formal { border-left: 3px solid #448aff !important; }
.style-border-sarcastic { border-left: 3px solid #b388ff !important; }
.style-border-tech { border-left: 3px solid #00e676 !important; }
.style-border-fun { border-left: 3px solid #ff6b35 !important; }

/* Score bars */
.score-bar-track {
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
    margin: 0.3rem 0;
}

.score-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 1s ease;
}

.score-high { background: #00e676; box-shadow: 0 0 8px rgba(0,230,118,0.3); }
.score-medium { background: #ffd740; box-shadow: 0 0 8px rgba(255,215,64,0.2); }
.score-low { background: #ed1c24; box-shadow: 0 0 8px rgba(237,28,36,0.3); }

/* Correction timeline */
.correction-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 3px solid #ed1c24;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}

.correction-item.pass {
    border-left-color: #00e676;
}

.correction-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.badge-improved { background: rgba(0,230,118,0.12); color: #00e676; }
.badge-same { background: rgba(255,215,64,0.12); color: #ffd740; }

/* Pipeline step indicators */
.pipeline-step-box {
    text-align: center;
    padding: 0.6rem 0.3rem;
    border-radius: 8px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.step-pending {
    background: rgba(255,255,255,0.02);
    color: #44445a;
    border: 1px solid rgba(255,255,255,0.04);
}

.step-active {
    background: rgba(237,28,36,0.12);
    color: #ff3b43;
    border: 1px solid rgba(237,28,36,0.2);
    animation: pulse 1.5s infinite;
}

.step-complete {
    background: rgba(0,230,118,0.08);
    color: #00e676;
    border: 1px solid rgba(0,230,118,0.15);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* Hide Streamlit defaults */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 999px; }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.8rem;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "history" not in st.session_state:
    st.session_state.history = []
if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = None
if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None


# ── Constants ─────────────────────────────────────────────────
STYLE_META = {
    "formal":            {"emoji": "🎩", "label": "Formal",    "css": "formal",    "color": "#448aff"},
    "sarcastic":         {"emoji": "😏", "label": "Sarcastic", "css": "sarcastic", "color": "#b388ff"},
    "humorous_tech":     {"emoji": "💻", "label": "Tech Humor","css": "tech",      "color": "#00e676"},
    "humorous_non_tech": {"emoji": "😂", "label": "Fun",       "css": "fun",       "color": "#ff6b35"},
}

PIPELINE_STEPS = [
    ("🎞️", "Frames"),
    ("🎵", "Audio"),
    ("🧠", "Perceive"),
    ("✍️", "Style"),
    ("⚖️", "Evaluate"),
    ("🔄", "Correct"),
    ("✅", "Done"),
]

STEP_KEYS = [
    "extracting_frames", "extracting_audio", "analyzing",
    "styling", "evaluating", "self_correction", "complete"
]


# ── Helper Functions ──────────────────────────────────────────

def get_score_class(score):
    """Return CSS class for score value."""
    if score >= 0.8: return "score-high"
    if score >= 0.5: return "score-medium"
    return "score-low"


def render_score_bar(label, score, color_class):
    """Render a horizontal score bar."""
    pct = int(score * 100)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <span style="width:100px; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#7a7a95;">{label}</span>
        <div class="score-bar-track" style="flex:1;">
            <div class="score-bar-fill {color_class}" style="width:{pct}%;"></div>
        </div>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:600; color:#b0b0c8; width:38px; text-align:right;">{score:.2f}</span>
    </div>
    """, unsafe_allow_html=True)


def build_radar_chart(scores_dict):
    """Build a Plotly radar chart from eval scores."""
    categories = []
    accuracy_vals = []
    style_vals = []

    for style_key, meta in STYLE_META.items():
        if style_key in scores_dict:
            s = scores_dict[style_key]
            acc = s.get("accuracy", 0) if isinstance(s, dict) else s.accuracy
            sty = s.get("style_match", 0) if isinstance(s, dict) else s.style_match
            categories.append(meta["label"])
            accuracy_vals.append(acc)
            style_vals.append(sty)

    # Close the polygon
    categories.append(categories[0])
    accuracy_vals.append(accuracy_vals[0])
    style_vals.append(style_vals[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=accuracy_vals, theta=categories,
        fill='toself', name='Accuracy',
        line_color='#448aff',
        fillcolor='rgba(68,138,255,0.15)',
    ))

    fig.add_trace(go.Scatterpolar(
        r=style_vals, theta=categories,
        fill='toself', name='Style Match',
        line_color='#00e676',
        fillcolor='rgba(0,230,118,0.1)',
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9, color='#44445a'),
                            gridcolor='rgba(255,255,255,0.05)'),
            angularaxis=dict(tickfont=dict(size=11, color='#7a7a95'),
                             gridcolor='rgba(255,255,255,0.05)'),
        ),
        showlegend=True,
        legend=dict(font=dict(size=11, color='#7a7a95'), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=30, b=30),
        height=340,
    )

    return fig


# ── Sidebar (History) ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Processing History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.container():
                st.markdown(f"**{item['filename']}**")
                st.caption(f"{item['timestamp']} · {item.get('status', 'complete')}")
                st.divider()
    else:
        st.caption("No videos processed yet.")

    st.divider()
    st.markdown("##### Configuration")
    st.code(f"Backend: {pipeline.INFERENCE_BACKEND}\nPerception: {pipeline.PERCEPTION_MODEL.split('/')[-1]}\nStyling: {pipeline.STYLING_MODEL.split('/')[-1]}", language="yaml")


# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎬 Rambler 3.0</div>
    <div class="hero-subtitle">AI Video Captioning Agent · Multi-Model Gemma Cascade</div>
    <div class="hero-team"><strong>Omnix</strong> · Abdelrahman Amr Ahmed Abdullah · AMD Hackathon Track 2</div>
</div>
""", unsafe_allow_html=True)


# ── Upload Section ────────────────────────────────────────────
if st.session_state.results is None:
    st.markdown("")
    col_pad_l, col_upload, col_pad_r = st.columns([1, 4, 1])
    with col_upload:
        uploaded_file = st.file_uploader(
            "📤 Upload your video clip (MP4, 30s–2min)",
            type=["mp4"],
            help="Drag and drop or click to browse. Max ~500MB.",
            key="video_uploader",
        )

        if uploaded_file is not None:
            # Show video preview
            st.video(uploaded_file)

            # Config columns
            c1, c2 = st.columns(2)
            with c1:
                eval_threshold = st.slider(
                    "Eval Threshold", 0.8, 1.0, 0.8, 0.05,
                    help="Captions scoring below this are re-generated (minimum 0.8/80%)"
                )
            with c2:
                max_rounds = st.slider(
                    "Max Correction Rounds", 1, 5, 3,
                    help="Max self-correction attempts per caption"
                )

            if st.button("🚀 Generate Captions", type="primary", use_container_width=True):
                # Save video to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                st.session_state.video_bytes = uploaded_file.getvalue()

                # Run pipeline with progress
                progress_bar = st.progress(0, text="Initializing pipeline...")

                # Pipeline step display
                step_cols = st.columns(len(PIPELINE_STEPS))
                step_placeholders = []
                for i, (icon, label) in enumerate(PIPELINE_STEPS):
                    with step_cols[i]:
                        ph = st.empty()
                        ph.markdown(f'<div class="pipeline-step-box step-pending">{icon}<br>{label}</div>',
                                    unsafe_allow_html=True)
                        step_placeholders.append(ph)

                detail_placeholder = st.empty()

                current_step_idx = [0]

                def on_progress(step, detail="", progress=0):
                    """Callback from pipeline to update Streamlit UI."""
                    progress_bar.progress(min(progress, 1.0), text=detail)

                    # Update step indicators
                    step_idx = STEP_KEYS.index(step) if step in STEP_KEYS else current_step_idx[0]

                    for i, (icon, label) in enumerate(PIPELINE_STEPS):
                        if i < step_idx:
                            step_placeholders[i].markdown(
                                f'<div class="pipeline-step-box step-complete">{icon}<br>{label}</div>',
                                unsafe_allow_html=True)
                        elif i == step_idx:
                            step_placeholders[i].markdown(
                                f'<div class="pipeline-step-box step-active">{icon}<br>{label}</div>',
                                unsafe_allow_html=True)

                    current_step_idx[0] = step_idx
                    detail_placeholder.caption(f"🔄 {detail}")

                # Run the pipeline
                with st.status("⚡ Running Gemma Cascade Pipeline...", expanded=True) as status:
                    try:
                        st.write("Starting video analysis...")
                        results = pipeline.run_pipeline(
                            video_path=tmp_path,
                            on_progress=on_progress,
                            eval_threshold=eval_threshold,
                            max_correction_rounds=max_rounds,
                        )

                        st.session_state.results = results
                        st.session_state.history.append({
                            "filename": uploaded_file.name,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "status": "complete",
                        })

                        status.update(label="✅ Pipeline Complete!", state="complete")
                        st.toast("🎉 Captions generated successfully!", icon="✅")
                        time.sleep(1)
                        st.rerun()

                    except Exception as e:
                        status.update(label=f"❌ Error: {str(e)[:100]}", state="error")
                        st.error(f"Pipeline failed: {str(e)}")
                        st.session_state.history.append({
                            "filename": uploaded_file.name,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "status": "error",
                        })

                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass


# ── Results Section ───────────────────────────────────────────
if st.session_state.results is not None:
    results = st.session_state.results
    captions = results.get("captions", {})
    scores = results.get("scores", {})
    initial_scores = results.get("initial_scores", {})
    correction_history = results.get("correction_history", [])
    thumbnails = results.get("thumbnails", [])
    raw_insights = results.get("raw_insights", "")

    # New Analysis button
    if st.button("🔄 Analyze Another Video", type="secondary"):
        st.session_state.results = None
        st.session_state.video_bytes = None
        st.rerun()

    st.divider()

    # ── Video + Captions ──────────────────────────────────────
    st.markdown("### 📝 Styled Captions")

    view_mode = st.radio(
        "Display Mode",
        ["🃏 Cards", "📊 Compare All"],
        horizontal=True, label_visibility="collapsed"
    )

    if view_mode == "🃏 Cards":
        col_video, col_captions = st.columns([1, 1], gap="medium")

        with col_video:
            if st.session_state.video_bytes:
                st.video(st.session_state.video_bytes)

        with col_captions:
            tabs = st.tabs([f"{m['emoji']} {m['label']}" for m in STYLE_META.values()])
            for i, (style_key, meta) in enumerate(STYLE_META.items()):
                with tabs[i]:
                    caption_text = ""
                    if isinstance(captions, dict):
                        caption_text = captions.get(style_key, "No caption generated")
                    elif hasattr(captions, style_key):
                        caption_text = getattr(captions, style_key, "")

                    border_class = f"style-border-{meta['css']}"
                    st.markdown(f"""
                    <div class="metric-card {border_class}">
                        <h4 class="style-{meta['css']}">{meta['emoji']} {meta['label']}</h4>
                        <p>{caption_text}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Score display for this style
                    if style_key in scores:
                        s = scores[style_key]
                        acc = s.get("accuracy", 0) if isinstance(s, dict) else getattr(s, 'accuracy', 0)
                        sty = s.get("style_match", 0) if isinstance(s, dict) else getattr(s, 'style_match', 0)
                        render_score_bar("Accuracy", acc, get_score_class(acc))
                        render_score_bar("Style Match", sty, get_score_class(sty))

    else:  # Compare All
        cols = st.columns(2, gap="medium")
        for i, (style_key, meta) in enumerate(STYLE_META.items()):
            with cols[i % 2]:
                caption_text = ""
                if isinstance(captions, dict):
                    caption_text = captions.get(style_key, "")
                elif hasattr(captions, style_key):
                    caption_text = getattr(captions, style_key, "")

                border_class = f"style-border-{meta['css']}"
                st.markdown(f"""
                <div class="metric-card {border_class}">
                    <h4 class="style-{meta['css']}">{meta['emoji']} {meta['label']}</h4>
                    <p>{caption_text}</p>
                </div>
                """, unsafe_allow_html=True)

                if style_key in scores:
                    s = scores[style_key]
                    acc = s.get("accuracy", 0) if isinstance(s, dict) else getattr(s, 'accuracy', 0)
                    sty = s.get("style_match", 0) if isinstance(s, dict) else getattr(s, 'style_match', 0)
                    st.caption(f"Accuracy: {acc:.2f} · Style: {sty:.2f}")

    st.divider()

    # ── Filmstrip ─────────────────────────────────────────────
    if thumbnails:
        st.markdown("### 🎞️ Keyframes")
        thumb_cols = st.columns(min(len(thumbnails), 8))
        for i, thumb_b64 in enumerate(thumbnails[:8]):
            with thumb_cols[i]:
                clean = thumb_b64.replace("data:image/jpeg;base64,", "")
                try:
                    st.image(base64.b64decode(clean), use_container_width=True)
                except Exception:
                    st.caption(f"Frame {i+1}")

    st.divider()

    # ── Eval Dashboard ────────────────────────────────────────
    st.markdown("### ⚖️ Gemma Eval Dashboard")

    eval_col1, eval_col2 = st.columns([1, 1], gap="medium")

    with eval_col1:
        # Serialize scores for radar chart
        scores_for_chart = {}
        for k, v in scores.items():
            if isinstance(v, dict):
                scores_for_chart[k] = v
            elif hasattr(v, 'accuracy'):
                scores_for_chart[k] = {"accuracy": v.accuracy, "style_match": v.style_match}

        if scores_for_chart:
            fig = build_radar_chart(scores_for_chart)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with eval_col2:
        st.markdown("##### Score Breakdown")
        for style_key, meta in STYLE_META.items():
            if style_key in scores:
                s = scores[style_key]
                acc = s.get("accuracy", 0) if isinstance(s, dict) else getattr(s, 'accuracy', 0)
                sty = s.get("style_match", 0) if isinstance(s, dict) else getattr(s, 'style_match', 0)
                st.markdown(f"**{meta['emoji']} {meta['label']}**")
                render_score_bar("Accuracy", acc, get_score_class(acc))
                render_score_bar("Style Match", sty, get_score_class(sty))
                st.markdown("")

    st.divider()

    # ── Self-Correction History ───────────────────────────────
    if correction_history:
        st.markdown("### 🔄 Self-Correction Timeline")
        for i, round_data in enumerate(correction_history):
            is_pass = round_data.get("passed", False)
            css_class = "pass" if is_pass else ""
            round_num = round_data.get("round", i + 1)
            detail = round_data.get("detail", "")
            styles_fixed = round_data.get("styles_corrected", [])

            with st.expander(
                f"{'✅' if is_pass else '🔄'} Round {round_num} — {'Passed' if is_pass else 'Corrected'}",
                expanded=(i == len(correction_history) - 1)
            ):
                if detail:
                    st.write(detail)
                if styles_fixed:
                    st.caption(f"Styles re-generated: {', '.join(styles_fixed)}")

                # Show round scores if available
                round_scores = round_data.get("scores", {})
                if round_scores:
                    score_cols = st.columns(len(round_scores))
                    for j, (sk, sv) in enumerate(round_scores.items()):
                        with score_cols[j]:
                            acc = sv.get("accuracy", 0) if isinstance(sv, dict) else getattr(sv, 'accuracy', 0)
                            sty = sv.get("style_match", 0) if isinstance(sv, dict) else getattr(sv, 'style_match', 0)
                            avg = (acc + sty) / 2
                            badge = "badge-improved" if avg >= 0.8 else "badge-same"
                            st.markdown(f"""
                            <span class="correction-badge {badge}">{STYLE_META.get(sk, {}).get('emoji', '')} {avg:.2f}</span>
                            """, unsafe_allow_html=True)

    st.divider()

    # ── Raw Insights (Collapsible) ────────────────────────────
    with st.expander("🧠 Raw Perception Output"):
        st.text(raw_insights if raw_insights else "No raw insights available.")

    st.divider()

    # ── Export ─────────────────────────────────────────────────
    st.markdown("### 💾 Export")

    export_cols = st.columns(3)

    # Prepare export data
    export_data = {
        "captions": captions if isinstance(captions, dict) else {
            k: getattr(captions, k, "") for k in STYLE_META.keys()
        },
        "scores": {k: (v if isinstance(v, dict) else {"accuracy": v.accuracy, "style_match": v.style_match})
                   for k, v in scores.items()},
        "correction_rounds": len(correction_history),
        "raw_insights": raw_insights,
        "pipeline_config": {
            "backend": pipeline.INFERENCE_BACKEND,
            "perception_model": pipeline.PERCEPTION_MODEL,
            "styling_model": pipeline.STYLING_MODEL,
            "eval_model": pipeline.EVAL_MODEL,
        },
    }

    with export_cols[0]:
        st.download_button(
            "💾 Download JSON",
            data=json.dumps(export_data, indent=2, default=str),
            file_name="rambler_results.json",
            mime="application/json",
            use_container_width=True,
        )

    with export_cols[1]:
        # Copy all captions as text
        all_text = "\n\n".join([
            f"[{STYLE_META[k]['label']}]\n{v}" if isinstance(v, str) else f"[{STYLE_META[k]['label']}]\n{v}"
            for k, v in (captions.items() if isinstance(captions, dict) else
                         {k: getattr(captions, k, "") for k in STYLE_META.keys()}.items())
        ])
        st.download_button(
            "📋 Download Captions (TXT)",
            data=all_text,
            file_name="rambler_captions.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with export_cols[2]:
        st.download_button(
            "📊 Download Scores (JSON)",
            data=json.dumps(export_data["scores"], indent=2, default=str),
            file_name="rambler_scores.json",
            mime="application/json",
            use_container_width=True,
        )


# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#44445a; font-size:0.72rem; padding:1rem;'>"
    "Rambler 3.0 · Team <strong style='color:#ed1c24;'>Omnix</strong> · AMD Hackathon Track 2 · "
    "Powered by Gemma on AMD ROCm"
    "</div>",
    unsafe_allow_html=True
)
