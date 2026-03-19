FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Zmienne wymagane dla NVIDIA Container Toolkit
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,video,utility
ENV IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg
ENV MOVIEPY_FFMPEG_BINARY=/usr/bin/ffmpeg

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3-dev \
    build-essential \
    ffmpeg \
    imagemagick \
    ghostscript \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# Fix for ImageMagick security policy (required for TextClip to work)
RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick*/policy.xml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

ENV KOMBAJN_STORAGE__SSD_ROOT=/data/ssd \
    KOMBAJN_STORAGE__USB_ROOT=/data/usb \
    KOMBAJN_STORAGE__HDD_ROOT=/data/hdd

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
