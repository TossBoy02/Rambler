# ============================================================
# Rambler 3.0 — Core Pipeline Module
# Team Omnix | AMD Hackathon Track 2: Video Captioning Agent
# Powered by Gemma via Fireworks AI
# ============================================================

import os
import cv2
import base64
import json
import tempfile
import subprocess
import requests
import time
from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Callable, Dict, Any


# ── Configuration ──────────────────────────────────────────────
INFERENCE_BACKEND = os.environ.get("INFERENCE_BACKEND", "fireworks")  # "fireworks" or "local"

if INFERENCE_BACKEND == "local":
    # Local vLLM on AMD GPU (ROCm) — free, no API key needed
    FIREWORKS_API_KEY = "not-needed"
    FIREWORKS_API_URL = os.environ.get("LOCAL_API_URL", "http://localhost:8080/v1/chat/completions")
    PERCEPTION_MODEL = os.environ.get("PERCEPTION_MODEL", "google/gemma-4-31b-it")
    STYLING_MODEL    = os.environ.get("STYLING_MODEL",    "google/gemma-4-31b-it")
    EVAL_MODEL       = os.environ.get("EVAL_MODEL",       "google/gemma-4-31b-it")
else:
    # Fireworks AI Cloud API
    FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")
    FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
    PERCEPTION_MODEL = os.environ.get("PERCEPTION_MODEL", "accounts/fireworks/models/gemma-4-31b-it")
    STYLING_MODEL    = os.environ.get("STYLING_MODEL",    "accounts/fireworks/models/gemma-4-26b-a4b-it")
    EVAL_MODEL       = os.environ.get("EVAL_MODEL",       "accounts/fireworks/models/gemma-4-26b-a4b-it")

# ── Pipeline Styles ────────────────────────────────────────────
ALL_STYLES = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]


# ── Pydantic Schemas ──────────────────────────────────────────

class StyleCaption(BaseModel):
    """A single styled caption."""
    caption: str

class StyledOutput(BaseModel):
    """Complete output with all four style captions."""
    formal: str = ""
    sarcastic: str = ""
    humorous_tech: str = ""
    humorous_non_tech: str = ""

class EvalScore(BaseModel):
    """Evaluation scores for a single style."""
    accuracy: float
    style_match: float

class EvalResult(BaseModel):
    """Complete evaluation result for all styles."""
    formal: EvalScore
    sarcastic: EvalScore
    humorous_tech: EvalScore
    humorous_non_tech: EvalScore


# ── Progress Callback Helper ──────────────────────────────────

def _noop_progress(step: str, detail: str = "", progress: float = 0):
    """Default no-op progress callback."""
    pass


# ── Stage 1: Ingestion Module ─────────────────────────────────

def extract_frames(video_path: str, fps: int = 1, max_frames: int = 30) -> List[str]:
    """
    Extract frames from video at the specified FPS rate.
    Returns list of Base64-encoded JPEG strings with data URI prefix.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0
    frame_interval = int(video_fps / fps) if fps > 0 else int(video_fps)

    frames_b64 = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            b64_str = base64.b64encode(buffer).decode('utf-8')
            frames_b64.append(f"data:image/jpeg;base64,{b64_str}")
        frame_idx += 1

    cap.release()

    # Subsample if too many frames
    if len(frames_b64) > max_frames:
        step = len(frames_b64) / max_frames
        frames_b64 = [frames_b64[int(i * step)] for i in range(max_frames)]

    return frames_b64


def extract_frames_thumbnails(video_path: str, count: int = 10) -> List[str]:
    """
    Extract thumbnail frames for the filmstrip display.
    Returns smaller Base64-encoded JPEG strings.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        cap.release()
        return []

    interval = max(1, total_frames // count)
    thumbnails = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval == 0 and len(thumbnails) < count:
            # Resize to thumbnail (160px wide)
            h, w = frame.shape[:2]
            new_w = 160
            new_h = int(h * (new_w / w))
            thumb = cv2.resize(frame, (new_w, new_h))
            _, buffer = cv2.imencode('.jpg', thumb, [cv2.IMWRITE_JPEG_QUALITY, 70])
            b64_str = base64.b64encode(buffer).decode('utf-8')
            thumbnails.append(f"data:image/jpeg;base64,{b64_str}")
        frame_idx += 1

    cap.release()
    return thumbnails


def extract_audio(video_path: str) -> Optional[str]:
    """
    Extract audio from video as mono 16kHz 32-bit float WAV.
    Returns Base64-encoded WAV string or None.
    """
    output_path = tempfile.mktemp(suffix='.wav')

    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-vn',
        '-acodec', 'pcm_f32le',
        '-ar', '16000',
        '-ac', '1',
        str(output_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return None
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return None

    with open(output_path, 'rb') as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

    # Cleanup temp file
    try:
        os.remove(output_path)
    except OSError:
        pass

    return audio_b64


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Get basic video metadata."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {}

    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }
    info["duration"] = info["total_frames"] / info["fps"] if info["fps"] > 0 else 0
    cap.release()
    return info


# ── Stage 2: Multimodal Perception (gemma-4-e4b-it) ──────────

ANALYSIS_PROMPT = """
You are an expert multimodal video analyst. You will receive a sequence of video 
frames (sampled at 1 frame per second) and optionally an audio track from a short 
video clip (30 seconds to 2 minutes long).

Perform a comprehensive analysis covering ALL of the following dimensions:

## 1. Visual Content Analysis
- **Scene Description**: What is happening in the video? Describe the setting, 
  objects, actions, and narrative arc across the frames.
- **Temporal Progression**: How does the scene evolve from start to end?
- **Visual Style**: Note any distinctive visual elements (lighting, colors, 
  camera angles, transitions).

## 2. Facial & Human Expression Analysis
- **Facial Tracking**: Identify any people visible and track their expressions 
  across frames.
- **Micro-Expressions**: Look carefully for subtle cues like forced smiles, 
  eyebrow drops, micro-smirks, eye rolls, or tension in the jaw.
- **Body Language**: Note posture, gestures, and physical engagement.
- **Emotional Arc**: How do the subjects' emotions evolve throughout the clip?

## 3. Environmental & Contextual Analysis
- **Setting**: Indoor/outdoor, time of day, weather, location type.
- **Atmosphere**: Overall mood conveyed by the environment.
- **Context Clues**: Any text, logos, signs, or cultural indicators visible.

## 4. Audio & Vocal Analysis (if audio is provided)
- **Speech Content**: Summarize any spoken words or dialogue.
- **Vocal Qualities**: Note tone, volume, inflection, pace, and emotional 
  undertones in the voice.
- **Sound Effects**: Identify background sounds, music, or ambient noise.
- **Audio-Visual Alignment**: How does the audio complement or contrast 
  with the visual content?

## 5. Overall Synthesis
- **Core Message**: What is the video trying to communicate?
- **Mood Summary**: The dominant emotional tone (e.g., cheerful, tense, 
  humorous, dramatic).
- **Key Moments**: Highlight 2-3 most significant moments in the clip.
- **Captioning Notes**: Provide specific details that would be useful for 
  writing captions in different tones (formal, sarcastic, humorous).

Be thorough, specific, and observant. Your analysis will be used to generate 
video captions in multiple styles, so include both objective facts and 
subjective impressions.
""".strip()


def build_multimodal_payload(
    frames_b64: List[str],
    audio_b64: Optional[str],
    prompt: str,
) -> dict:
    """Build the API-ready payload for Fireworks AI multimodal endpoint."""
    content_parts = []

    content_parts.append({
        "type": "text",
        "text": f"Analyze this video ({len(frames_b64)} frames at 1fps). "
                f"{'Audio track is included.' if audio_b64 else 'No audio track available — focus on visual analysis.'}"
    })

    for frame in frames_b64:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": frame}
        })

    if audio_b64:
        content_parts.append({
            "type": "input_audio",
            "input_audio": {
                "data": audio_b64,
                "format": "wav"
            }
        })

    payload = {
        "model": PERCEPTION_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content_parts}
        ],
        "max_tokens": 4096,
        "temperature": 0.7
    }

    return payload


def analyze_video(payload: dict) -> str:
    """Send multimodal payload to Fireworks AI for deep video analysis."""
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        FIREWORKS_API_URL,
        headers=headers,
        json=payload,
        timeout=300
    )

    if response.status_code != 200:
        error_detail = response.text[:500]
        raise RuntimeError(f"Perception API Error {response.status_code}: {error_detail}")

    result = response.json()
    raw_insights = result["choices"][0]["message"]["content"]
    return raw_insights


# ── Stage 3: Structural Synthesizer (gemma-4-26b-a4b-it) ─────

STRUCTURING_PROMPT = """
You are a creative copywriter and JSON formatting specialist. You will receive 
a detailed multimodal analysis of a short video clip. Your task is to generate 
captions in EXACTLY four distinct styles.

## Style Definitions

1. **formal**: Professional, objective, broadcast-quality tone. Think CNN/BBC 
   news anchor. No humor, no slang. Precise and informative.

2. **sarcastic**: Dry, witty, eye-rolling tone. Think a comedian doing commentary. 
   Use irony, understatement, and sharp observations. Be clever, not mean.

3. **humorous_tech**: Nerd/tech humor. Use programming references, tech jargon 
   jokes, Silicon Valley culture, Stack Overflow memes, or gaming references. 
   Make developers laugh.

4. **humorous_non_tech**: Everyday, accessible humor. Think sitcom commentary, 
   dad jokes, pop culture references, relatable observations. Anyone should 
   find this funny.

## CRITICAL RULES
- Each style MUST sound distinctly different from the others
- Each caption should be 2-4 engaging sentences
- ALL four styles must reference the same video content accurately
- The humor must be ORIGINAL and CREATIVE, not generic
- The captions should feel natural, not forced

## Required JSON Schema
You MUST output valid JSON matching this exact schema:

{
  "formal": "Your formal caption here...",
  "sarcastic": "Your sarcastic caption here...",
  "humorous_tech": "Your tech humor caption here...",
  "humorous_non_tech": "Your everyday humor caption here..."
}

Output ONLY the JSON object. No markdown fences, no explanations.
""".strip()


def structure_output(raw_insights: str, styles: List[str] = None, max_retries: int = 3) -> dict:
    """Convert raw analysis into structured styled captions JSON."""
    if styles is None:
        styles = ALL_STYLES

    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(1, max_retries + 1):
        payload = {
            "model": STYLING_MODEL,
            "messages": [
                {"role": "system", "content": STRUCTURING_PROMPT},
                {
                    "role": "user",
                    "content": f"Here is the detailed video analysis. Generate the four styled captions:\n\n{raw_insights}"
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 2048,
            "temperature": 0.8
        }

        response = requests.post(
            FIREWORKS_API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            continue

        result = response.json()
        raw_json_str = result["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(raw_json_str)
            # Ensure all styles are present
            captions = {}
            for style in styles:
                if style in parsed:
                    val = parsed[style]
                    # Handle both string and dict formats
                    if isinstance(val, dict):
                        captions[style] = val.get("caption", val.get("text", str(val)))
                    else:
                        captions[style] = str(val)
                else:
                    captions[style] = ""

            # Verify we have content for all styles
            if all(captions.get(s) for s in styles):
                return captions

        except (json.JSONDecodeError, ValidationError):
            continue

    raise RuntimeError(f"Failed to generate valid captions after {max_retries} attempts")


# ── Stage 4: Gemma Eval Self-Correction ───────────────────────

EVAL_PROMPT = """
You are a strict caption quality judge. You will receive:
1. A video analysis (ground truth about what the video shows)
2. Four styled captions for that video

Score EACH caption on exactly two dimensions (0.0 to 1.0):

1. **accuracy** (0.0–1.0): How faithfully does the caption reflect the actual video content?
   - 1.0 = perfectly describes what happens in the video
   - 0.5 = gets the gist but misses key details or adds wrong info
   - 0.0 = completely unrelated to the video

2. **style_match** (0.0–1.0): How well does the caption match its designated tone?
   - formal: Professional, objective, no humor (1.0 = BBC News quality)
   - sarcastic: Dry wit, irony, sharp observations (1.0 = stand-up comedian)
   - humorous_tech: Programming/tech jokes (1.0 = r/ProgrammerHumor gold)
   - humorous_non_tech: Everyday humor, dad jokes (1.0 = sitcom narration)

Output valid JSON matching this exact schema:
{
  "formal": {"accuracy": 0.0, "style_match": 0.0},
  "sarcastic": {"accuracy": 0.0, "style_match": 0.0},
  "humorous_tech": {"accuracy": 0.0, "style_match": 0.0},
  "humorous_non_tech": {"accuracy": 0.0, "style_match": 0.0}
}

Be strict and honest. Output ONLY the JSON object.
""".strip()


def gemma_eval(captions: dict, raw_insights: str) -> dict:
    """
    Use Gemma to evaluate caption quality.
    Returns scores dict with accuracy and style_match per style.
    """
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    eval_input = (
        f"## Video Analysis (Ground Truth):\n{raw_insights}\n\n"
        f"## Captions to Evaluate:\n{json.dumps(captions, indent=2)}"
    )

    payload = {
        "model": EVAL_MODEL,
        "messages": [
            {"role": "system", "content": EVAL_PROMPT},
            {"role": "user", "content": eval_input}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 512,
        "temperature": 0.2
    }

    try:
        response = requests.post(
            FIREWORKS_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return _default_scores()

        result = response.json()
        scores = json.loads(result["choices"][0]["message"]["content"])

        # Validate and normalize scores
        validated = {}
        for style in ALL_STYLES:
            if style in scores and isinstance(scores[style], dict):
                validated[style] = {
                    "accuracy": max(0.0, min(1.0, float(scores[style].get("accuracy", 0.5)))),
                    "style_match": max(0.0, min(1.0, float(scores[style].get("style_match", 0.5)))),
                }
            else:
                validated[style] = {"accuracy": 0.5, "style_match": 0.5}

        return validated

    except Exception:
        return _default_scores()


def _default_scores() -> dict:
    """Return default scores when eval fails."""
    return {style: {"accuracy": 0.5, "style_match": 0.5} for style in ALL_STYLES}


REGEN_PROMPT_TEMPLATE = """
You are a creative copywriter. A previous caption for a video was scored poorly.

## Video Analysis:
{insights}

## Previous Caption (style: {style}):
{old_caption}

## Feedback:
- Accuracy score: {accuracy:.2f}/1.0 — {"needs better factual accuracy" if accuracy < 0.8 else "acceptable"}
- Style match score: {style_match:.2f}/1.0 — {"needs stronger {style} tone" if style_match < 0.8 else "acceptable"}

## Your Task:
Write a BETTER caption in the **{style}** style that:
1. Accurately describes what happens in the video
2. Strongly matches the {style} tone
3. Is 2-4 engaging sentences

Style guide for {style}:
{style_guide}

Output ONLY the new caption text. No JSON, no markdown, no explanations.
"""

STYLE_GUIDES = {
    "formal": "Professional, objective, broadcast-quality. Think CNN/BBC news anchor. No humor, no slang.",
    "sarcastic": "Dry, witty, eye-rolling. Use irony, understatement, sharp observations. Clever, not mean.",
    "humorous_tech": "Programming references, tech jargon jokes, Silicon Valley humor, Stack Overflow memes.",
    "humorous_non_tech": "Sitcom commentary, dad jokes, pop culture references, relatable observations.",
}


def self_correct(
    captions: dict,
    raw_insights: str,
    scores: dict,
    threshold: float = 0.8,
    max_rounds: int = 3,
    on_progress: Callable = None,
) -> dict:
    """
    Self-correction loop: re-generate captions that score below threshold.
    Returns tuple of (final_captions, correction_history).
    """
    if on_progress is None:
        on_progress = _noop_progress

    history = []
    current_captions = dict(captions)
    current_scores = dict(scores)

    for round_num in range(1, max_rounds + 1):
        # Find styles that need correction
        failing_styles = []
        for style in ALL_STYLES:
            s = current_scores.get(style, {})
            acc = s.get("accuracy", 0.5)
            sm = s.get("style_match", 0.5)
            if acc < threshold or sm < threshold:
                failing_styles.append(style)

        if not failing_styles:
            break

        on_progress(
            "self_correction",
            f"Round {round_num}: Re-generating {', '.join(failing_styles)}",
            round_num / max_rounds
        )

        history.append({
            "round": round_num,
            "failing_styles": failing_styles,
            "scores_before": {s: current_scores[s] for s in failing_styles},
        })

        # Re-generate each failing style
        headers = {
            "Authorization": f"Bearer {FIREWORKS_API_KEY}",
            "Content-Type": "application/json"
        }

        for style in failing_styles:
            s = current_scores[style]
            regen_prompt = REGEN_PROMPT_TEMPLATE.format(
                insights=raw_insights[:2000],
                style=style,
                old_caption=current_captions[style],
                accuracy=s["accuracy"],
                style_match=s["style_match"],
                style_guide=STYLE_GUIDES[style],
            )

            payload = {
                "model": STYLING_MODEL,
                "messages": [
                    {"role": "user", "content": regen_prompt}
                ],
                "max_tokens": 512,
                "temperature": 0.85
            }

            try:
                response = requests.post(
                    FIREWORKS_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    new_caption = result["choices"][0]["message"]["content"].strip()
                    # Remove any wrapping quotes
                    if new_caption.startswith('"') and new_caption.endswith('"'):
                        new_caption = new_caption[1:-1]
                    current_captions[style] = new_caption
            except Exception:
                pass

        # Re-evaluate
        current_scores = gemma_eval(current_captions, raw_insights)

        # Record scores after correction
        history[-1]["scores_after"] = {s: current_scores[s] for s in failing_styles}

    return current_captions, current_scores, history


# ── Full Pipeline Orchestrator ────────────────────────────────

def run_full_pipeline(
    video_path: str,
    styles: List[str] = None,
    on_progress: Callable = None,
    eval_threshold: float = 0.8,
    max_correction_rounds: int = 3,
) -> dict:
    """
    Run the complete Rambler 3.0 pipeline.

    Returns dict with:
        - captions: {style: caption_text}
        - scores: {style: {accuracy, style_match}}
        - correction_history: list of correction rounds
        - video_info: metadata about the video
        - thumbnails: list of thumbnail base64 strings
        - raw_insights: the analysis text
    """
    if styles is None:
        styles = ALL_STYLES
    if on_progress is None:
        on_progress = _noop_progress

    video_path = str(video_path)

    # Step 1: Video Info
    on_progress("video_info", "Reading video metadata...", 0.05)
    info = get_video_info(video_path)

    # Step 2: Extract Frames
    on_progress("extracting_frames", f"Extracting frames at 1fps...", 0.1)
    frames = extract_frames(video_path, fps=1, max_frames=30)

    # Step 3: Extract Thumbnails
    on_progress("extracting_thumbnails", "Generating filmstrip thumbnails...", 0.15)
    thumbnails = extract_frames_thumbnails(video_path, count=12)

    # Step 4: Extract Audio
    on_progress("extracting_audio", "Extracting audio track...", 0.2)
    audio = extract_audio(video_path)

    # Step 5: Build Payload
    on_progress("building_payload", "Building multimodal payload...", 0.25)
    payload = build_multimodal_payload(frames, audio, ANALYSIS_PROMPT)

    # Step 6: Multimodal Analysis
    on_progress("analyzing", "Running Gemma perception analysis...", 0.3)
    raw_insights = analyze_video(payload)

    # Step 7: Generate Styled Captions
    on_progress("styling", "Generating styled captions...", 0.55)
    captions = structure_output(raw_insights, styles=styles)

    # Step 8: Gemma Eval
    on_progress("evaluating", "Running Gemma evaluation...", 0.7)
    scores = gemma_eval(captions, raw_insights)

    # Step 9: Self-Correction Loop
    on_progress("self_correction", "Self-correction loop...", 0.8)
    final_captions, final_scores, correction_history = self_correct(
        captions, raw_insights, scores,
        threshold=eval_threshold,
        max_rounds=max_correction_rounds,
        on_progress=on_progress,
    )

    on_progress("complete", "Pipeline complete!", 1.0)

    return {
        "captions": final_captions,
        "scores": final_scores,
        "correction_history": correction_history,
        "initial_scores": scores,
        "video_info": info,
        "thumbnails": thumbnails,
        "raw_insights": raw_insights,
    }

# Alias for compatibility with app.py
run_pipeline = run_full_pipeline
