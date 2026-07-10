#!/usr/bin/env python3
"""
Rambler — Unified Docker Launcher
Team Omnix | AMD Hackathon Track 2

Detects the presence of /input/tasks.json (headless evaluation mode)
and runs entrypoint.py. Otherwise, starts the Streamlit interactive UI.
"""

import os
import sys
import subprocess


def main():
    # If user provides explicit commands/arguments, run them directly
    if len(sys.argv) > 1:
        print(f"📦 Executing custom command: {' '.join(sys.argv[1:])}")
        try:
            result = subprocess.run(sys.argv[1:])
            sys.exit(result.returncode)
        except Exception as e:
            print(f"❌ Failed to run command: {e}")
            sys.exit(1)

    # Auto-detect mode based on hackathon input file presence
    tasks_path = "/input/tasks.json"
    if os.path.exists(tasks_path):
        print("📋 /input/tasks.json detected! Running in headless evaluation mode...")
        try:
            result = subprocess.run(["python", "docker/entrypoint.py"])
            sys.exit(result.returncode)
        except Exception as e:
            print(f"❌ Failed to run entrypoint.py: {e}")
            sys.exit(1)
    else:
        print("🚀 Starting Streamlit Web Application on port 8501...")
        try:
            result = subprocess.run([
                "streamlit", "run", "app.py",
                "--server.port=8501",
                "--server.address=0.0.0.0",
                "--server.headless=true"
            ])
            sys.exit(result.returncode)
        except Exception as e:
            print(f"❌ Failed to run Streamlit app: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
