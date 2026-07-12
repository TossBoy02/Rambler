# ============================================================
# Rambler — Streamlit Demo Application
# Team Omnix | AMD Hackathon Track 2
# Powered by Gemma via Fireworks AI
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
    page_title="Rambler — AI Video Captioning | Team Omnix",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Base64 Logo Loader ────────────────────────────────────────
def get_base64_logo():
    """Load the project logo and convert it to base64 for HTML embedding."""
    try:
        logo_path = Path("logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
    except Exception:
        pass
    return ""

logo_b64 = get_base64_logo()

# ── Custom CSS (Ultra-Premium AMD Vibe) ──────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* Global overrides for dark workstation theme */
.stApp {{
    background: #020208;
    background-image: 
        radial-gradient(ellipse 50% 50% at 50% -10%, rgba(237, 28, 36, 0.15) 0%, transparent 80%),
        radial-gradient(ellipse 40% 40% at 85% 85%, rgba(255, 107, 53, 0.04) 0%, transparent 70%),
        linear-gradient(rgba(255, 255, 255, 0.006) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.006) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px;
    font-family: 'Inter', sans-serif;
    color: #eeeef2;
}}

/* Header section styling */
.hero-header {{
    text-align: center;
    padding: 2.5rem 0 2rem;
    position: relative;
}}

.hero-header::after {{
    content: '';
    display: block;
    margin: 1.5rem auto 0;
    width: 50%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(237, 28, 36, 0.5), rgba(255, 107, 53, 0.2), rgba(237, 28, 36, 0.5), transparent);
}}

.hero-brand-container {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    margin-bottom: 0.5rem;
}}

.hero-logo-img {{
    height: 64px;
    width: 64px;
    object-fit: contain;
    border-radius: 50%;
    filter: drop-shadow(0 0 16px rgba(237, 28, 36, 0.45));
    animation: pulseGlow 4s ease-in-out infinite alternate;
}}

@keyframes pulseGlow {{
    0% {{ filter: drop-shadow(0 0 8px rgba(237, 28, 36, 0.35)); }}
    100% {{ filter: drop-shadow(0 0 20px rgba(237, 28, 36, 0.6)); }}
}}

.hero-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 3.5rem;
    font-weight: 900;
    color: #ed1c24;
    -webkit-text-fill-color: initial;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin: 0;
}}

.hero-subtitle {{
    color: #8c8c9e;
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 0.2rem;
    letter-spacing: 0.02em;
}}

.hero-team {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    color: #7a7a95;
    font-family: 'JetBrains Mono', monospace;
    padding: 0.35rem 1.2rem;
    border: 1px solid rgba(237, 28, 36, 0.25);
    border-radius: 999px;
    background: rgba(237, 28, 36, 0.04);
    margin-top: 0.6rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}

.hero-team strong {{
    color: #ff3b43;
    font-weight: 700;
}}

/* Premium Glass Cards with AMD Red Accents */
.metric-card {{
    background: rgba(10, 10, 22, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}}

.metric-card:hover {{
    border-color: rgba(237, 28, 36, 0.25);
    background: rgba(15, 15, 30, 0.75);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(237, 28, 36, 0.08), 0 8px 24px rgba(0,0,0,0.6);
}}

.metric-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}}

.metric-card h4 {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
}}

.metric-card p {{
    font-size: 0.92rem;
    line-height: 1.75;
    color: #e2e2ee;
}}

/* AMD Vibe Style-specific border-glow colors */
.style-formal {{ color: #448aff !important; }}
.style-sarcastic {{ color: #b388ff !important; }}
.style-tech {{ color: #00e676 !important; }}
.style-fun {{ color: #ff6b35 !important; }}

.style-border-formal {{ border-left: 4px solid #448aff !important; }}
.style-border-sarcastic {{ border-left: 4px solid #b388ff !important; }}
.style-border-tech {{ border-left: 4px solid #00e676 !important; }}
.style-border-fun {{ border-left: 4px solid #ff6b35 !important; }}

/* Workstation Score progress bars */
.score-bar-track {{
    background: rgba(255,255,255,0.04);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin: 0.4rem 0;
}}

.score-bar-fill {{
    height: 100%;
    border-radius: 999px;
    transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}}

.score-high {{ background: #00e676; box-shadow: 0 0 8px rgba(0,230,118,0.4); }}
.score-medium {{ background: #ffd740; box-shadow: 0 0 8px rgba(255,215,64,0.3); }}
.score-low {{ background: #ed1c24; box-shadow: 0 0 8px rgba(237,28,36,0.5); }}

/* Self-Correction History Timeline */
.correction-item {{
    background: rgba(12, 12, 26, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-left: 4px solid #ed1c24;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: all 0.2s ease;
}}

.correction-item:hover {{
    background: rgba(18, 18, 36, 0.5);
    border-color: rgba(237, 28, 36, 0.2);
    border-left-color: #ff3b43;
}}

.correction-item.pass {{
    border-left-color: #00e676;
}}

.correction-badge {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
}}

.badge-improved {{ background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.2); }}
.badge-same {{ background: rgba(255,215,64,0.12); color: #ffd740; border: 1px solid rgba(255,215,64,0.2); }}

/* Pipeline steps dynamic style */
.pipeline-step-box {{
    text-align: center;
    padding: 0.8rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}}

.step-pending {{
    background: rgba(255,255,255,0.01);
    color: #4b4b66;
    border: 1px solid rgba(255,255,255,0.03);
}}

.step-active {{
    background: rgba(237,28,36,0.18);
    color: #ff3b43;
    border: 1px solid rgba(237,28,36,0.4);
    box-shadow: 0 0 15px rgba(237, 28, 36, 0.25);
    animation: pulseRed 2s infinite alternate;
}}

.step-complete {{
    background: rgba(0,230,118,0.08);
    color: #00e676;
    border: 1px solid rgba(0,230,118,0.2);
}}

@keyframes pulseRed {{
    0% {{ transform: scale(1); box-shadow: 0 0 8px rgba(237, 28, 36, 0.15); }}
    100% {{ transform: scale(1.03); box-shadow: 0 0 20px rgba(237, 28, 36, 0.35); }}
}}

/* Sidebar Design Elements */
[data-testid="stSidebar"] {{
    background-color: #06060f !important;
    border-right: 1px solid rgba(237, 28, 36, 0.15);
}}

.sidebar-header {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #eeeef2;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.sidebar-run-card {{
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 0.65rem 0.8rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
    cursor: pointer;
}}

.sidebar-run-card:hover {{
    border-color: rgba(237, 28, 36, 0.3);
    background: rgba(237, 28, 36, 0.03);
}}

/* Styled tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: rgba(255,255,255,0.015);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid rgba(255,255,255,0.03);
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 8px 16px;
    color: #8c8c9e;
    transition: all 0.2s ease;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: #eeeef2;
    background: rgba(255,255,255,0.03);
}}

.stTabs [aria-selected="true"] {{
    background: rgba(237, 28, 36, 0.12) !important;
    color: #ff3b43 !important;
    border: 1px solid rgba(237, 28, 36, 0.25) !important;
}}

/* File uploader dynamic glow */
[data-testid="stFileUploader"] {{
    border: 2px dashed rgba(237, 28, 36, 0.25);
    background: rgba(10, 10, 22, 0.4);
    border-radius: 20px;
    padding: 2.25rem 2rem;
    transition: all 0.3s ease;
}}

[data-testid="stFileUploader"]:hover {{
    border-color: rgba(237, 28, 36, 0.6);
    background: rgba(237, 28, 36, 0.02);
    box-shadow: 0 0 24px rgba(237, 28, 36, 0.05);
}}

/* Custom buttons styling */
.stButton>button {{
    border-radius: 10px;
    font-weight: 700;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
}}

.stButton>button[kind="primary"] {{
    background: linear-gradient(135deg, #ed1c24 0%, #ff5252 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(237, 28, 36, 0.3) !important;
    color: white !important;
}}

.stButton>button[kind="primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(237, 28, 36, 0.45) !important;
}}

.stButton>button[kind="secondary"] {{
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #8c8c9e !important;
}}

.stButton>button[kind="secondary"]:hover {{
    color: #eeeef2 !important;
    border-color: rgba(237, 28, 36, 0.3) !important;
    background: rgba(237, 28, 36, 0.02) !important;
}}
/* Custom sidebar styling on the left side of the viewport */
section[data-testid="stSidebar"] {{
    border-right: 2px solid rgba(237, 28, 36, 0.4) !important;
    border-left: none !important;
    box-shadow: 10px 0 45px rgba(0,0,0,0.85) !important;
    background-color: rgba(8, 8, 18, 0.95) !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
}}

/* Add padding to sidebar content so it doesn't overlap the right edge bar */
[data-testid="stSidebarUserContent"] {{
    padding-right: 35px !important;
}}

/* Collapsed state: vertical clear bar on left edge of viewport */
[data-testid="stCollapsedSidebarCollapsed"] {{
    left: 0 !important;
    right: auto !important;
    position: fixed !important;
    top: 0 !important;
    height: 100vh !important;
    width: 25px !important;
    background: rgba(10, 10, 22, 0.05) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-left: none !important;
    z-index: 99999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

[data-testid="stCollapsedSidebarCollapsed"]:hover {{
    background: rgba(237, 28, 36, 0.12) !important;
    border-right: 1px solid rgba(237, 28, 36, 0.5) !important;
    box-shadow: 4px 0 20px rgba(237, 28, 36, 0.2) !important;
}}

[data-testid="stCollapsedSidebarCollapsed"] button {{
    height: 100% !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

[data-testid="stCollapsedSidebarCollapsed"] svg {{
    color: rgba(122, 122, 149, 0.4) !important;
    transition: all 0.3s ease !important;
}}

[data-testid="stCollapsedSidebarCollapsed"]:hover svg {{
    color: #ff3b43 !important;
    transform: scale(1.3) !important;
}}

/* Expanded state: vertical clear bar on the right edge of open sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
    position: absolute !important;
    right: 0 !important;
    left: auto !important;
    top: 0 !important;
    height: 100vh !important;
    width: 25px !important;
    background: rgba(10, 10, 22, 0.05) !important;
    border-left: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-right: none !important;
    border-radius: 0 !important;
    z-index: 99999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover {{
    background: rgba(237, 28, 36, 0.12) !important;
    border-left: 1px solid rgba(237, 28, 36, 0.5) !important;
    box-shadow: -4px 0 20px rgba(237, 28, 36, 0.2) !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {{
    height: 100% !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {{
    color: rgba(122, 122, 149, 0.4) !important;
    transition: all 0.3s ease !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover svg {{
    color: #ff3b43 !important;
    transform: scale(1.3) !important;
}}
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
if "show_history" not in st.session_state:
    st.session_state.show_history = False
if "tasks_results" not in st.session_state:
    st.session_state.tasks_results = None
if "results_json_data" not in st.session_state:
    st.session_state.results_json_data = None
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
    if score >= 0.9: return "score-high"
    if score >= 0.8: return "score-high"
    if score >= 0.5: return "score-medium"
    return "score-low"


def render_score_bar(label, score, color_class):
    """Render a horizontal score bar."""
    pct = int(score * 100)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <span style="width:100px; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#8c8c9e;">{label}</span>
        <div class="score-bar-track" style="flex:1;">
            <div class="score-bar-fill {color_class}" style="width:{pct}%;"></div>
        </div>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:600; color:#eeeef2; width:38px; text-align:right;">{score:.2f}</span>
    </div>
    """, unsafe_allow_html=True)


def build_radar_chart(scores_dict):
    """Build a Plotly radar chart from eval scores configured in AMD brand colors."""
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
        fill='toself', name='Accuracy (Factual)',
        line_color='#ed1c24',
        fillcolor='rgba(237, 28, 36, 0.2)',
    ))

    fig.add_trace(go.Scatterpolar(
        r=style_vals, theta=categories,
        fill='toself', name='Style Match',
        line_color='#ffab40',
        fillcolor='rgba(255, 171, 64, 0.1)',
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True, range=[0, 1], 
                tickfont=dict(size=9, color='#7a7a95'),
                gridcolor='rgba(255,255,255,0.05)',
                linecolor='rgba(255,255,255,0.05)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#eeeef2', family='Outfit'),
                gridcolor='rgba(255,255,255,0.05)'
            ),
        ),
        showlegend=True,
        legend=dict(font=dict(size=11, color='#eeeef2'), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=30, b=30),
        height=320,
    )

    return fig


def render_run_results(results, video_bytes=None, video_url=None, key_suffix=""):
    """Modular function to render the full pipeline results visualization."""
    captions = results.get("captions", {})
    scores = results.get("scores", {})
    initial_scores = results.get("initial_scores", {})
    correction_history = results.get("correction_history", [])
    thumbnails = results.get("thumbnails", [])
    raw_insights = results.get("raw_insights", "")

    # ── Video + Captions ──────────────────────────────────────
    st.markdown("### 📝 Styled Captions")

    view_mode = st.radio(
        "Display Mode",
        ["🃏 Cards Mode", "📊 Compare All Modes"],
        horizontal=True, label_visibility="collapsed",
        key=f"view_mode_{key_suffix}"
    )

    if "Cards" in view_mode:
        col_video, col_captions = st.columns([1, 1], gap="medium")

        with col_video:
            if video_bytes:
                st.video(video_bytes)
            elif video_url:
                st.video(video_url)

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

                    st.markdown("<br/>", unsafe_allow_html=True)

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
                <div class="metric-card {border_class}" style="margin-bottom: 1.25rem;">
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
        scores_for_chart = {}
        for k, v in scores.items():
            if isinstance(v, dict):
                scores_for_chart[k] = v
            elif hasattr(v, 'accuracy'):
                scores_for_chart[k] = {"accuracy": v.accuracy, "style_match": v.style_match}

        if scores_for_chart:
            fig = build_radar_chart(scores_for_chart)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"radar_chart_{key_suffix}")

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
        st.markdown("### 🔄 Self-Correction Timeline (Threshold >= 0.8)")
        for i, round_data in enumerate(correction_history):
            is_pass = round_data.get("passed", False)
            round_num = round_data.get("round", i + 1)
            detail = round_data.get("detail", "")
            styles_fixed = round_data.get("styles_corrected", [])

            with st.expander(
                f"{'✅' if is_pass else '🔄'} Round {round_num} — {'Passed' if is_pass else 'Refinement Active'}",
                expanded=(i == len(correction_history) - 1)
            ):
                if detail:
                    st.write(detail)
                if styles_fixed:
                    st.caption(f"Styles re-evaluated & re-generated: {', '.join(styles_fixed)}")

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
    with st.expander("🧠 Raw Perception Output", expanded=False):
        st.text(raw_insights if raw_insights else "No raw insights available.")

    st.divider()

    # ── Export ─────────────────────────────────────────────────
    st.markdown("### 💾 Export Outputs")

    export_cols = st.columns(3)

    export_data = {
        "captions": captions if isinstance(captions, dict) else {
            k: getattr(captions, k, "") for k in STYLE_META.keys()
        },
        "scores": {k: (v if isinstance(v, dict) else {"accuracy": v.accuracy, "style_match": v.style_match})
                   for k, v in scores.items()},
        "correction_rounds": len(correction_history),
        "raw_insights": raw_insights,
        "pipeline_config": {
            "backend": "fireworks",
            "model": pipeline.GEMMA_MODEL,
        },
    }

    with export_cols[0]:
        st.download_button(
            "💾 Download JSON",
            data=json.dumps(export_data, indent=2, default=str),
            file_name=f"rambler_results_{key_suffix}.json" if key_suffix else "rambler_results.json",
            mime="application/json",
            use_container_width=True,
            key=f"dl_json_{key_suffix}"
        )

    with export_cols[1]:
        all_text = "\n\n".join([
            f"[{STYLE_META[k]['label']}]\n{v}" if isinstance(v, str) else f"[{STYLE_META[k]['label']}]\n{v}"
            for k, v in (captions.items() if isinstance(captions, dict) else
                         {k: getattr(captions, k, "") for k in STYLE_META.keys()}.items())
        ])
        st.download_button(
            "📋 Download Captions (TXT)",
            data=all_text,
            file_name=f"rambler_captions_{key_suffix}.txt" if key_suffix else "rambler_captions.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"dl_txt_{key_suffix}"
        )

    with export_cols[2]:
        st.download_button(
            "📊 Download Scores (JSON)",
            data=json.dumps(export_data["scores"], indent=2, default=str),
            file_name=f"rambler_scores_{key_suffix}.json" if key_suffix else "rambler_scores.json",
            mime="application/json",
            use_container_width=True,
            key=f"dl_scores_{key_suffix}"
        )



# ── Header (AMD Dynamic Logo Layout) ──────────────────────────
if logo_b64:
    header_html = f"""
    <div class="hero-header">
        <div class="hero-brand-container">
            <img class="hero-logo-img" src="data:image/png;base64,{logo_b64}" />
            <div class="hero-title" style="color: #ed1c24; background: none; -webkit-text-fill-color: initial;">Rambler</div>
        </div>
        <div class="hero-subtitle">AI Video Captioning Agent · Multi-Model Gemma Cascade</div>
        <div class="hero-team"><strong>Omnix</strong> · Abdelrahman Amr Ahmed Abdullah · AMD Hackathon Track 2</div>
    </div>
    """
else:
    header_html = """
    <div class="hero-header">
        <div class="hero-brand-container">
            <div class="hero-title" style="color: #ed1c24; background: none; -webkit-text-fill-color: initial;">🎬 Rambler</div>
        </div>
        <div class="hero-subtitle">AI Video Captioning Agent · Multi-Model Gemma Cascade</div>
        <div class="hero-team"><strong>Omnix</strong> · Abdelrahman Amr Ahmed Abdullah · AMD Hackathon Track 2</div>
    </div>
    """
st.markdown(header_html, unsafe_allow_html=True)

# ── Sidebar (Caption & Video History) ─────────────────────────
with st.sidebar:
    st.markdown('<h3 style="font-family:\'Outfit\'; margin-top: 0; color: #eeeef2;">📋 Caption History</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.8rem; color:#7a7a95; margin-bottom: 1.5rem;">Select a past run to restore its results and video state.</p>', unsafe_allow_html=True)
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.75rem;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #eeeef2; line-height: 1.25; word-break: break-all;">{item['filename']}</div>
                <div style="font-size: 0.7rem; color: #7a7a95; font-family: 'JetBrains Mono', monospace; margin-top: 0.25rem;">{item['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("👁️ View Run", key=f"load_sidebar_hist_{i}", use_container_width=True, help="Load this run"):
                st.session_state.results = item["results"]
                st.session_state.video_bytes = item["video_bytes"]
                st.rerun()
            st.markdown("<hr style='border:0; height:1px; background:rgba(255,255,255,0.05); margin:0.8rem 0;' />", unsafe_allow_html=True)
            
        st.markdown("")
        if st.button("🗑️ Clear History", key="clear_history_sidebar", use_container_width=True):
            st.session_state.history = []
            st.session_state.results = None
            st.session_state.video_bytes = None
            st.toast("History cleared", icon="🗑️")
            st.rerun()
    else:
        st.caption("No caption runs found in this session.")


# ── Upload Section ────────────────────────────────────────────
if st.session_state.results is None and st.session_state.tasks_results is None:
    st.markdown("")
    col_pad_l, col_upload, col_pad_r = st.columns([1, 4, 1])
    with col_upload:
        upload_tab_single, upload_tab_batch = st.tabs(["🎥 Single Video Upload", "📋 tasks.json Batch Mode"])
        
        with upload_tab_single:
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
                            
                            # Append the full result and video bytes to history list for full loading
                            st.session_state.history.append({
                                "filename": uploaded_file.name,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "status": "complete",
                                "results": results,
                                "video_bytes": st.session_state.video_bytes
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
                                "results": None,
                                "video_bytes": None
                            })

                        finally:
                            # Clean up temp file
                            try:
                                os.unlink(tmp_path)
                            except OSError:
                                pass

        with upload_tab_batch:
            tasks_file = st.file_uploader(
                "📥 Upload tasks.json file",
                type=["json"],
                help="Upload the hackathon evaluation tasks file.",
                key="tasks_uploader",
            )
            
            if tasks_file is not None:
                try:
                    tasks_data = json.loads(tasks_file.getvalue().decode('utf-8'))
                    st.success(f"Successfully loaded {len(tasks_data)} task(s) from JSON.")
                    
                    # Display preview of tasks in an expander
                    with st.expander("🔍 View Tasks Detail", expanded=True):
                        for i, t in enumerate(tasks_data):
                            st.markdown(f"**Task #{i+1}: {t.get('task_id', 'unknown')}**")
                            st.markdown(f"- Video URL: `{t.get('video_url', '')}`")
                            st.markdown(f"- Requested Styles: `{', '.join(t.get('styles', []))}`")
                    
                    # Save to input/tasks.json
                    input_dir = Path("/input")
                    if not input_dir.exists():
                        input_dir = Path("input")
                    input_dir.mkdir(parents=True, exist_ok=True)
                    tasks_path = input_dir / "tasks.json"
                    with open(tasks_path, "w", encoding="utf-8") as f:
                        json.dump(tasks_data, f, indent=2, ensure_ascii=False)
                    
                    # Settings for processing
                    c1, c2 = st.columns(2)
                    with c1:
                        batch_eval_threshold = st.slider(
                            "Eval Threshold (Batch)", 0.8, 1.0, 0.8, 0.05,
                            help="Captions scoring below this are re-generated (minimum 0.8/80%)",
                            key="batch_eval_threshold_slider"
                        )
                    with c2:
                        batch_max_rounds = st.slider(
                            "Max Correction Rounds (Batch)", 1, 5, 3,
                            help="Max self-correction attempts per caption",
                            key="batch_max_rounds_slider"
                        )
                    
                    if st.button("🚀 Process Batch Tasks", type="primary", use_container_width=True):
                        # Run the batch process
                        progress_bar = st.progress(0, text="Starting batch process...")
                        
                        batch_results = []
                        results_json_output = []
                        
                        import requests
                        for idx, t in enumerate(tasks_data):
                            task_id = t["task_id"]
                            video_url = t["video_url"]
                            styles = t.get("styles", pipeline.ALL_STYLES)
                            
                            progress_bar.progress(idx / len(tasks_data), text=f"Processing task {task_id} ({idx+1}/{len(tasks_data)})...")
                            
                            with st.status(f"⚡ Processing Task `{task_id}`...", expanded=True) as status:
                                status.write(f"⏳ Downloading video from {video_url}...")
                                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                                    tmp_path = tmp.name
                                    try:
                                        dl_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
                                        res = requests.get(video_url, stream=True, timeout=300, headers=dl_headers)
                                        res.raise_for_status()
                                        for chunk in res.iter_content(chunk_size=8192):
                                            tmp.write(chunk)
                                    except Exception as e:
                                        status.update(label=f"❌ Error: Task `{task_id}` Download Failed", state="error")
                                        st.error(f"Download failed: {str(e)}")
                                        batch_results.append({
                                            "task_id": task_id,
                                            "video_url": video_url,
                                            "video_bytes": None,
                                            "error": f"Download failed: {e}",
                                            "results": None
                                        })
                                        continue
                                
                                # Pipeline step display (matching single video mode)
                                step_cols = st.columns(len(PIPELINE_STEPS))
                                step_placeholders = []
                                for si, (icon, label) in enumerate(PIPELINE_STEPS):
                                    with step_cols[si]:
                                        ph = st.empty()
                                        ph.markdown(f'<div class="pipeline-step-box step-pending">{icon}<br>{label}</div>',
                                                    unsafe_allow_html=True)
                                        step_placeholders.append(ph)

                                detail_placeholder = st.empty()
                                current_step_idx = [0]

                                # Run pipeline
                                status.write("🧠 Running cascade pipeline...")
                                try:
                                    def on_progress(step, detail="", progress=0):
                                        status.write(f"⚙️ [{progress*100:.0f}%] {step}: {detail}")
                                        # Update pipeline step boxes
                                        step_idx_val = STEP_KEYS.index(step) if step in STEP_KEYS else current_step_idx[0]
                                        for si2, (icon2, label2) in enumerate(PIPELINE_STEPS):
                                            if si2 < step_idx_val:
                                                step_placeholders[si2].markdown(
                                                    f'<div class="pipeline-step-box step-complete">{icon2}<br>{label2}</div>',
                                                    unsafe_allow_html=True)
                                            elif si2 == step_idx_val:
                                                step_placeholders[si2].markdown(
                                                    f'<div class="pipeline-step-box step-active">{icon2}<br>{label2}</div>',
                                                    unsafe_allow_html=True)
                                        current_step_idx[0] = step_idx_val
                                        detail_placeholder.caption(f"🔄 {detail}")
                                    
                                    run_res = pipeline.run_full_pipeline(
                                        video_path=tmp_path,
                                        styles=styles,
                                        eval_threshold=batch_eval_threshold,
                                        max_correction_rounds=batch_max_rounds,
                                        on_progress=on_progress,
                                    )
                                    
                                    # Mark all steps complete
                                    for si3, (icon3, label3) in enumerate(PIPELINE_STEPS):
                                        step_placeholders[si3].markdown(
                                            f'<div class="pipeline-step-box step-complete">{icon3}<br>{label3}</div>',
                                            unsafe_allow_html=True)
                                    detail_placeholder.caption("✅ Pipeline complete!")
                                    
                                    # Format for results.json
                                    captions_out = {s: run_res["captions"].get(s, "") for s in styles}
                                    results_json_output.append({
                                        "task_id": task_id,
                                        "captions": captions_out
                                    })
                                    
                                    # Read video bytes for Streamlit playback
                                    with open(tmp_path, "rb") as vf:
                                        vid_bytes = vf.read()
                                    
                                    # Keep full result metadata for display
                                    batch_results.append({
                                        "task_id": task_id,
                                        "video_url": video_url,
                                        "video_bytes": vid_bytes,
                                        "results": run_res
                                    })
                                    status.update(label=f"✅ Task `{task_id}` Complete!", state="complete")
                                except Exception as e:
                                    status.update(label=f"❌ Error: Task `{task_id}` Pipeline Failed", state="error")
                                    st.error(f"Pipeline failed: {str(e)}")
                                    batch_results.append({
                                        "task_id": task_id,
                                        "video_url": video_url,
                                        "video_bytes": None,
                                        "error": f"Pipeline failed: {e}",
                                        "results": None
                                    })
                                finally:
                                    try:
                                        os.unlink(tmp_path)
                                    except OSError:
                                        pass
                        
                        progress_bar.progress(1.0, text="Batch processing complete!")
                        
                        # Save to /output/results.json (or output/results.json)
                        output_dir = Path("/output")
                        if not output_dir.exists():
                            output_dir = Path("output")
                        output_dir.mkdir(parents=True, exist_ok=True)
                        results_path = output_dir / "results.json"
                        with open(results_path, "w", encoding="utf-8") as f:
                            json.dump(results_json_output, f, indent=2, ensure_ascii=False)
                        
                        # Save in session state for UI display
                        st.session_state.tasks_results = batch_results
                        st.session_state.results_json_data = json.dumps(results_json_output, indent=2, ensure_ascii=False)
                        st.toast("🎉 Batch completed successfully!", icon="✅")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error parsing tasks.json: {e}")


# ── Batch Results Section ─────────────────────────────────────
if st.session_state.tasks_results:
    st.markdown("### 📋 Batch Process Results")
    
    # Dashboard metrics row
    total_tasks = len(st.session_state.tasks_results)
    successful_tasks = sum(1 for tr in st.session_state.tasks_results if not tr.get("error"))
    
    # Calculate average scores
    total_acc = 0.0
    total_sty = 0.0
    score_count = 0
    for tr in st.session_state.tasks_results:
        if not tr.get("error") and tr.get("results"):
            t_scores = tr["results"].get("scores", {})
            for sk, s in t_scores.items():
                acc = s.get("accuracy", 0) if isinstance(s, dict) else getattr(s, 'accuracy', 0)
                sty = s.get("style_match", 0) if isinstance(s, dict) else getattr(s, 'style_match', 0)
                total_acc += acc
                total_sty += sty
                score_count += 1
                
    avg_acc = (total_acc / score_count) if score_count > 0 else 0.0
    avg_sty = (total_sty / score_count) if score_count > 0 else 0.0
    success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Render dashboard metrics in custom cards
    st.markdown("#### 📊 Evaluation Summary Dashboard")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card style-border-formal" style="margin-bottom: 1.25rem;">
            <h4 style="margin:0; color:#448aff;">📁 Total Tasks</h4>
            <h2 style="margin:5px 0 0 0; color:#eeeef2;">{total_tasks}</h2>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card style-border-sarcastic" style="margin-bottom: 1.25rem;">
            <h4 style="margin:0; color:#b388ff;">✅ Successful</h4>
            <h2 style="margin:5px 0 0 0; color:#eeeef2;">{successful_tasks} <span style="font-size:0.8rem; color:#7a7a95;">/ {total_tasks}</span></h2>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card style-border-tech" style="margin-bottom: 1.25rem;">
            <h4 style="margin:0; color:#00e676;">🎯 Avg Accuracy</h4>
            <h2 style="margin:5px 0 0 0; color:#eeeef2;">{avg_acc:.2f} <span style="font-size:0.8rem; color:#7a7a95;">(80% min)</span></h2>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-card style-border-fun" style="margin-bottom: 1.25rem;">
            <h4 style="margin:0; color:#ff6b35;">📈 Success Rate</h4>
            <h2 style="margin:5px 0 0 0; color:#eeeef2;">{success_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Header download and back buttons
    c_back, c_dl = st.columns([1, 2])
    with c_back:
        if st.button("🔄 Process Another Batch", type="secondary", use_container_width=True):
            st.session_state.tasks_results = None
            st.session_state.results_json_data = None
            st.rerun()
            
    with c_dl:
        st.download_button(
            label="📥 Download results.json",
            data=st.session_state.results_json_data,
            file_name="results.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
        
    st.divider()
    
    # Render tabs for each task result
    task_tabs = st.tabs([f"Task: {tr['task_id']}" for tr in st.session_state.tasks_results])
    
    for idx, tr in enumerate(st.session_state.tasks_results):
        with task_tabs[idx]:
            task_id = tr["task_id"]
            video_url = tr["video_url"]
            vid_bytes = tr["video_bytes"]
            run_res = tr["results"]
            
            st.markdown(f"#### 🎬 Task Detail: `{task_id}`")
            st.caption(f"Video Source: {video_url}")
            st.markdown("")
            
            if tr.get("error"):
                st.error(f"❌ Processing failed for this task: {tr['error']}")
            else:
                render_run_results(run_res, video_bytes=vid_bytes, key_suffix=f"task_{task_id}")


# ── Results Section ───────────────────────────────────────────
if st.session_state.results is not None:
    results = st.session_state.results
    
    # Clean action layout
    c_back, c_space = st.columns([1, 4])
    with c_back:
        if st.button("🔄 Analyze Another Video", type="secondary"):
            st.session_state.results = None
            st.session_state.video_bytes = None
            st.rerun()

    st.divider()

    render_run_results(results, video_bytes=st.session_state.video_bytes, key_suffix="single_run")


# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#5c5c7a; font-size:0.75rem; padding:1.5rem;'>"
    "Rambler · Team <strong style='color:#ff3b43;'>Omnix</strong> · AMD Hackathon Track 2 · "
    "Powered by Gemma via Fireworks AI"
    "</div>",
    unsafe_allow_html=True
)
