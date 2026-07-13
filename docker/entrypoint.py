#!/usr/bin/env python3
"""
Rambler — Headless Docker Entrypoint
Team Omnix | AMD Hackathon Track 2

Reads /input/tasks.json, processes each video, writes /output/results.json.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# Ensure stdout and stderr handle emojis and UTF-8 characters without crashing on Windows or non-UTF-8 terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import tempfile
import requests
import pipeline


def download_video(url: str, output_path: str) -> bool:
    """Download a video from URL to local path."""
    try:
        print(f"  ⬇️  Downloading: {url}")
        dl_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        response = requests.get(url, stream=True, timeout=300, headers=dl_headers)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ✅ Downloaded: {size_mb:.1f} MB")
        return True

    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return False


def process_task(task: dict) -> dict:
    """Process a single task from tasks.json."""
    task_id = task["task_id"]
    video_url = task["video_url"]
    styles = task.get("styles", pipeline.ALL_STYLES)

    print(f"\n{'='*60}")
    print(f"📋 Task: {task_id}")
    print(f"🎬 Video: {video_url}")
    print(f"🎨 Styles: {', '.join(styles)}")
    print(f"{'='*60}")

    # Download video to temp file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        if not download_video(video_url, tmp_path):
            return {
                "task_id": task_id,
                "captions": {s: "" for s in styles}
            }

        # Run pipeline
        def on_progress(step, detail="", progress=0):
            print(f"  [{progress*100:.0f}%] {step}: {detail}")

        result = pipeline.run_full_pipeline(
            video_path=tmp_path,
            styles=styles,
            on_progress=on_progress,
            eval_threshold=0.8,
            max_correction_rounds=2,
        )

        # Build output in required format
        captions = {}
        for style in styles:
            captions[style] = result["captions"].get(style, "")

        return {
            "task_id": task_id,
            "captions": captions,
        }

    finally:
        # Cleanup temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def main():
    print("\n🎬 Rambler — Team Omnix")
    print("AMD Hackathon Track 2: Video Captioning Agent")
    print(f"Model: {pipeline.GEMMA_MODEL}")
    print(f"API Key: {'✅ Set' if pipeline.FIREWORKS_API_KEY else '❌ NOT SET'}")

    if not pipeline.FIREWORKS_API_KEY:
        print("\n⚠️  WARNING: FIREWORKS_API_KEY environment variable not set!")
        print("Pass it with: docker run -e FIREWORKS_API_KEY=<your_key> ...")
        print("Continuing anyway — API calls will fail.\n")

    # Read tasks
    tasks_path = Path("/input/tasks.json")
    if not tasks_path.exists():
        print(f"\n❌ Tasks file not found: {tasks_path}")
        sys.exit(1)

    with open(tasks_path, 'r') as f:
        tasks = json.load(f)

    print(f"\n📋 Found {len(tasks)} task(s) to process")

    # Process each task — NEVER skip a task
    results = []
    for i, task in enumerate(tasks, 1):
        print(f"\n\n{'#'*60}")
        print(f"  Processing [{i}/{len(tasks)}]")
        print(f"{'#'*60}")

        try:
            result = process_task(task)
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error processing task {task.get('task_id', '?')}: {e}")
            # IMPORTANT: Still add a result with empty captions — never skip tasks
            results.append({
                "task_id": task.get("task_id", "unknown"),
                "captions": {s: "" for s in task.get("styles", pipeline.ALL_STYLES)}
            })

    # Write output
    output_dir = Path("/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "results.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'='*60}")
    print(f"✅ COMPLETE: {len(results)} tasks processed")
    print(f"💾 Output: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
