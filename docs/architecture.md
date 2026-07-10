# 🎬 Rambler — Architecture Diagram

This document provides a visual representation of the Rambler pipeline and deployment architectures.

---

## 1. Pipeline Execution Flow

The flowchart below visualizes the 6-stage multi-model Gemma cascade, showing data transformations and the self-correction feedback loop.

```mermaid
flowchart TD
    classDef stage fill:#0d0e1b,stroke:#ff6b35,stroke-width:2px,color:#eeeef2;
    classDef decision fill:#1b1d36,stroke:#ffab40,stroke-width:2px,color:#eeeef2;
    classDef data fill:#06060e,stroke:#448aff,stroke-width:1px,stroke-dasharray: 5 5,color:#7a7a95;
    classDef action fill:#ed1c24,stroke:#ff3b43,stroke-width:1px,color:#fff;

    %% Input
    A([🎥 Input Video File]) --> B[🛠️ Preprocessing Layer]
    
    %% Stage 1 & 2
    subgraph Preprocessing ["Stage 1 & 2: Local Feature Extraction"]
        B --> C[🎞️ Frame Extractor<br/>1 FPS JPEG]
        B --> D[🎵 Audio Extractor<br/>16kHz WAV]
    end
    
    C --> E[📦 Multimodal Payload]
    D --> E
    
    %% Stage 3
    E --> F["🧠 Stage 3: Perception Layer<br/>(Gemma 4 27B-IT)"]:::stage
    F --> G[📝 Raw Scene Insights]:::data
    
    %% Stage 4
    G --> H["✍️ Stage 4: Styling Layer<br/>(Gemma 4 26B-A4B-IT)"]:::stage
    H --> I["{ JSON Captions }<br/>(Formal, Sarcastic, Tech, Fun)"]:::data
    
    %% Stage 5
    I --> J["⚖️ Stage 5: Evaluation Judge<br/>(Gemma 4 26B-A4B-IT)"]:::stage
    J --> K[📊 Factual & Style Scores]:::data
    
    %% Stage 6
    K --> L{"❓ Threshold Check<br/>(Score >= 0.8?)"}:::decision
    
    L -- "Yes (Pass)" --> M[✅ Final Caption Output]
    L -- "No (Fail)" --> N["🔄 Stage 6: Self-Correction Loop"]:::stage
    
    N --> O["📝 Re-Generation Prompt<br/>(With targeted feedback)"]:::data
    O --> P["✍️ Re-Generate Caption<br/>(Gemma 4 26B-A4B-IT)"]:::stage
    P --> Q{🔄 Max Rounds Reached?}:::decision
    
    Q -- "No" --> J
    Q -- "Yes" --> M

    class A,B,C,D,E,M,O data;
    class L,Q decision;
```

---

## 2. Dynamic Sequence Diagram

The sequence diagram below shows how client interactions, the orchestration layer, and the backends (Fireworks AI vs. local vLLM) interact.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Judge
    participant App as Streamlit Application (app.py)
    participant Pipe as Pipeline Orchestrator (pipeline.py)
    participant Backend as Inference Backend (vLLM / Fireworks)

    User->>App: Upload Video & Set Parameters (Threshold >= 0.8)
    App->>Pipe: Trigger run_pipeline()
    activate Pipe
    
    Pipe->>Pipe: Extract Frames (OpenCV) & Audio (FFmpeg)
    Pipe->>Backend: Request Multimodal Perception (Gemma-4-31b-it)
    Backend-->>Pipe: Return Raw Scene Insights
    
    Pipe->>Backend: Request Style Synthesis (Gemma-4-26b-a4b-it)
    Backend-->>Pipe: Return JSON Styled Captions (4 Styles)
    
    rect rgb(20, 20, 40)
        note right of Pipe: Evaluation & Self-Correction Loop
        Pipe->>Backend: Request Evaluation Scoring
        Backend-->>Pipe: Return Accuracy & Style Scores
        
        alt Any Score < 0.8 and Round < Max Rounds
            Pipe->>Backend: Request Re-generation with Feedback
            Backend-->>Pipe: Return Corrected Caption
        end
    end
    
    Pipe-->>App: Return Final Results (Captions, Scores, History)
    deactivate Pipe
    
    App->>User: Render Dashboard (Video, Overlay/Cards, Plotly Radar Chart)
```

---

## 3. Hybrid Deployment Setup

Rambler dynamically routes inference requests based on the configured environment.

```
                  ┌───────────────────────────────┐
                  │        Rambler App            │
                  └──────────────┬────────────────┘
                                 │
                   Reads INFERENCE_BACKEND env
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
       INFERENCE_BACKEND=local       INFERENCE_BACKEND=fireworks
                 │                               │
        ┌────────▼────────┐             ┌────────▼────────┐
        │   Local Port    │             │  Fireworks AI   │
        │   (vLLM/ROCm)   │             │   Cloud API     │
        └────────┬────────┘             └────────┬────────┘
                 │                               │
        ┌────────▼────────┐             ┌────────▼────────┐
        │  AMD Instinct   │             │  Dedicated GPU  │
        │   MI300X GPU    │             │   (H200/B200)   │
        └─────────────────┘             └─────────────────┘
```
