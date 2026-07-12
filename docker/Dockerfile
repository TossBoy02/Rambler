FROM python:3.11-slim

# Install FFmpeg and system dependencies for OpenCV/Streamlit
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port for Streamlit (interactive mode)
EXPOSE 8501

# FIREWORKS_API_KEY must be passed at runtime:
#   docker run -e FIREWORKS_API_KEY=<key> ...
ENV FIREWORKS_API_KEY=""

# Entrypoint: auto-detects headless (if /input/tasks.json exists) or Streamlit mode
ENTRYPOINT ["python", "docker/launcher.py"]
