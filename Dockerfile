FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

ENV KOMBAJN_STORAGE__SSD_ROOT=/data/ssd \
    KOMBAJN_STORAGE__USB_ROOT=/data/usb \
    KOMBAJN_STORAGE__HDD_ROOT=/data/hdd

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

