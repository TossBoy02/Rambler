# 🎬 Rambler 3.0 — AI Video Captioning Agent

**Team Omnix** · Abdelrahman Amr Ahmed Abdullah
AMD Hackathon Track 2 | Powered by Gemma on AMD ROCm

---

## Short Description

> AI video captioning agent that uses a multi-model Gemma cascade to analyze video frames and audio, generate captions in 4 distinct styles (formal, sarcastic, humorous-tech, humorous-non-tech), self-evaluate with confidence scoring, and auto-correct low-quality outputs — all running on AMD hardware via ROCm.

---

## Long Description

**Rambler 3.0** is an intelligent video captioning pipeline that goes far beyond simple transcription. Given any short video clip (30s–2min), it performs deep multimodal analysis — extracting visual frames at 1fps, capturing audio waveforms, and synthesizing both modalities through Google's Gemma 4 model family running on AMD Instinct GPUs with ROCm.

### The Problem

Existing video captioning tools produce generic, one-size-fits-all descriptions. Content creators, accessibility teams, and media producers need captions that match specific tones — a formal news clip needs broadcast-quality narration, while a social media reel benefits from humor or sarcasm. Manual styling is time-consuming and inconsistent.

### Our Solution

Rambler 3.0 implements a **three-stage AI pipeline** that mirrors how a human editor would work:

1. **Perception Stage** (`gemma-4-27b-it`): A multimodal Gemma model ingests sampled video frames and extracted audio simultaneously, producing a comprehensive scene analysis covering visual content, facial micro-expressions, environmental context, vocal qualities, and emotional arcs.
2. **Styling Stage** (`gemma-4-26b-a4b-it`): A text-optimized Gemma model transforms the raw analysis into four distinct caption styles — **Formal** (BBC-quality narration), **Sarcastic** (dry wit and irony), **Humorous Tech** (programming jokes and Silicon Valley references), and **Humorous Non-Tech** (dad jokes and pop culture references).
3. **Self-Correction Stage** (`gemma-4-26b-a4b-it`): A Gemma-powered evaluation judge scores each caption on accuracy (0–1) and style fidelity (0–1). Captions falling below a 0.8 threshold are automatically regenerated with targeted feedback for up to 3 correction rounds, ensuring consistently high quality.

### Key Features

- **Multi-Model Gemma Cascade** — Different Gemma variants optimized for each pipeline stage
- **Multimodal Ingestion** — Processes both video frames (OpenCV) and audio waveforms (FFmpeg)
- **Facial Micro-Expression Analysis** — Detects subtle emotional cues like forced smiles and eyebrow drops
- **Self-Correcting Agent Loop** — Gemma evaluates its own outputs and iteratively improves them
- **Confidence Radar Charts** — Visual dashboard showing accuracy and style-match scores
- **Dual Caption Display** — View captions as subtitle overlays on video or side-by-side comparison cards
- **Interactive Demo** — Streamlit web app with drag-and-drop upload and real-time progress tracking
- **AMD ROCm Native** — Designed to run directly on AMD Instinct GPUs for maximum performance
- **Docker Submission** — Headless pipeline for automated hackathon evaluation

### Target Audience

Content creators, video producers, accessibility teams, social media managers, and anyone who needs stylistically diverse captions generated automatically from video content.

### Technology Stack

`Gemma 4` · `AMD ROCm` · `vLLM` · `Fireworks AI` · `Python` · `Streamlit` · `OpenCV` · `FFmpeg` · `Docker`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Streamlit Web App (app.py)                             │
│  ├── Video Upload (drag & drop)                         │
│  ├── Real-Time Pipeline Progress                        │
│  ├── Caption Display (overlay / cards / comparison)     │
│  ├── Gemma Eval Radar Chart (Plotly)                    │
│  ├── Self-Correction History Timeline                   │
│  └── Export (JSON / Clipboard)                          │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  Pipeline Engine (pipeline.py)                          │
│  ├── Stage 1: Frame Extraction (OpenCV, 1fps)           │
│  ├── Stage 2: Audio Extraction (FFmpeg, 16kHz WAV)      │
│  ├── Stage 3: Multimodal Perception (Gemma 4 27B)       │
│  │   └── Frames + Audio → Deep Scene Analysis           │
│  ├── Stage 4: Style Synthesis (Gemma 4 26B-A4B)         │
│  │   └── Analysis → 4 Styled Captions (JSON)            │
│  ├── Stage 5: Gemma Eval (Gemma 4 26B-A4B)              │
│  │   └── Captions → Accuracy + Style Scores             │
│  └── Stage 6: Self-Correction Loop                      │
│      └── Re-generate captions below 0.8 threshold       │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  Inference Backend (configurable)                       │
│  ├── Option A: AMD GPU + vLLM + ROCm (local)            │
│  └── Option B: Fireworks AI API (cloud)                  │
└─────────────────────────────────────────────────────────┘
```

---

## Multimodal Payload Structure

### Frame Extraction

```python
# Extract frames at 1fps, encode as base64 JPEG
frames = extract_frames(video_path, fps=1, max_frames=30)
# Each frame: "data:image/jpeg;base64,/9j/4AAQ..."
```

### Audio Extraction

```python
# Extract mono 16kHz 32-bit float WAV via FFmpeg
audio_b64 = extract_audio(video_path)
# Encoded as: base64 WAV string
```

### Multimodal API Payload

```json
{
  "model": "accounts/fireworks/models/gemma-4-27b-it",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert multimodal video analyst..."
    },
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Analyze this video (30 frames at 1fps)..."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
        {"type": "input_audio", "input_audio": {"data": "<base64_wav>", "format": "wav"}}
      ]
    }
  ],
  "max_tokens": 4096,
  "temperature": 0.7
}
```

---

## System Prompts

### Perception Prompt (Stage 3)

Analyzes 5 dimensions: Visual Content, Facial/Human Expressions, Environmental Context, Audio/Vocal Analysis, and Overall Synthesis. Full prompt in `pipeline.py`.

### Styling Prompt (Stage 4)

Generates captions in 4 styles: Formal (BBC-quality), Sarcastic (dry wit), Humorous Tech (programmer humor), Humorous Non-Tech (everyday humor). Outputs strict JSON.

### Eval Prompt (Stage 5)

Scores each caption on accuracy (0–1) and style_match (0–1). Strict scoring rubric with clear examples for each score level.

### Self-Correction Prompt (Stage 6)

Targeted re-generation prompt with specific feedback on which dimension failed and the style guide for the target tone.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- FFmpeg installed and on PATH
- (Optional) AMD GPU with ROCm for local inference

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rambler-3.0.git
cd rambler-3.0

# Install dependencies
pip install -r requirements.txt

# Configure API key (if using Fireworks AI)
cp .env.example .env
# Edit .env with your FIREWORKS_API_KEY

# Run the Streamlit app
streamlit run app.py
```

### Running on AMD Developer Cloud

```bash
# On the AMD AI Notebook (notebooks.amd.com/hackathon):
git clone https://github.com/YOUR_USERNAME/rambler-3.0.git
cd rambler-3.0
pip install -r requirements.txt

# Option A: Use Fireworks API
echo 'FIREWORKS_API_KEY=your_key' > .env
echo 'INFERENCE_BACKEND=fireworks' >> .env

# Option B: Run Gemma locally on AMD GPU
pip install vllm
vllm serve google/gemma-4-27b-it --port 8080 &
echo 'INFERENCE_BACKEND=local' > .env

# Start the demo
streamlit run app.py
```

### Docker (Headless Evaluation)

```bash
docker build -t rambler-3.0 -f docker/Dockerfile .
docker run -v /path/to/input:/input -v /path/to/output:/output \
  -e FIREWORKS_API_KEY=your_key rambler-3.0
```

---

## Project Structure

```
rambler-3.0/
├── app.py                  # Streamlit demo application
├── pipeline.py             # Core captioning pipeline
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # This file
├── docker/
│   ├── Dockerfile          # Hackathon submission image
│   └── entrypoint.py       # Headless task runner
└── sample_videos/          # Test video clips
```

---

## Team

| Member                                   | Role                         |
| ---------------------------------------- | ---------------------------- |
| **Abdelrahman Amr Ahmed Abdullah** | Solo Developer — Team Omnix |

---

## Hackathon

- **Event**: AMD Pervasive AI Developer Contest (lablab.ai)
- **Track**: Track 2 — Video Captioning Agent
- **Models**: Google Gemma 4 (27B-IT, 26B-A4B-IT)
- **Hardware**: AMD Instinct GPUs with ROCm
- **API**: Fireworks AI

---

## License

MIT License — see [LICENSE](LICENSE) for details.
