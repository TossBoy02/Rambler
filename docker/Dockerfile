FROM python:3.11-slim

# Install FFmpeg and system dependencies for OpenCV/Streamlit
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Entrypoint wrapper that switches modes automatically
ENTRYPOINT ["python", "docker/launcher.py"]
