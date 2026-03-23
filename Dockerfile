FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    imagemagick \
    ghostscript \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Fix for ImageMagick security policy
RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick*/policy.xml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

ENV KOMBAJN_STORAGE__SSD_ROOT=/data/ssd \
    KOMBAJN_STORAGE__USB_ROOT=/data/usb \
    KOMBAJN_STORAGE__HDD_ROOT=/data/hdd \
    PYTHONPATH=.

EXPOSE 8000 8501 5555 8081

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
