# Universal Docker Configuration (Hardware Agnostic)

Dla systemu "Kombajn AI" używamy teraz podejścia z `runtime: nvidia`. Pozwala to na trzymanie jednego pliku `docker-compose.yml` dla wszystkich środowisk (Windows/Intel oraz Xubuntu/NVIDIA).

## Wymagania środowiskowe
Na każdej maszynie (host) musi być zainstalowany `nvidia-container-toolkit`.
- Na Xubuntu: `sudo apt-get install -y nvidia-container-toolkit`
- Na Windows (WSL2): Instalujemy toolkit wewnątrz dystrybucji WSL2.

Jeśli Toolkit jest zainstalowany, a karta NVIDIA nie zostanie wykryta (np. Intel UHD), Docker automatycznie zignoruje flagę `runtime: nvidia` i uruchomi kontener w trybie CPU bez błędów.

## Dockerfile
```dockerfile
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
```

## Docker-Compose (Universal)
```yaml
x-worker-base: &worker-base
  build:
    context: .
    dockerfile: Dockerfile
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
    - NVIDIA_DRIVER_CAPABILITIES=compute,video,utility
    - KOMBAJN_REDIS_BROKER_URL=redis://redis:6379/0
    - KOMBAJN_REDIS_RESULT_BACKEND=redis://redis:6379/1
    - KOMBAJN_DRY_RUN=false
    - PYTHONPATH=.
  volumes:
    - .:/app
    - ./data/ssd:/data/ssd
    - ./data/usb:/data/usb
    - ./data/hdd:/data/hdd
    - ./data/projects:/data/projects
    - ./data/assets:/data/assets
  depends_on:
    redis:
      condition: service_healthy

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: kombajn_api
    command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - KOMBAJN_REDIS_BROKER_URL=redis://redis:6379/0
      - KOMBAJN_REDIS_RESULT_BACKEND=redis://redis:6379/1
      - PYTHONPATH=.
    depends_on:
      redis:
        condition: service_healthy

  scenario_ui:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: kombajn_scenario_ui
    command: streamlit run backend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    volumes:
      - .:/app
    ports:
      - "8501:8501"
    environment:
      - KOMBAJN_API_BASE=http://api:8000
      - PYTHONPATH=.
    depends_on:
      - api

  worker_io:
    <<: *worker-base
    container_name: kombajn_worker_io
    command: celery -A backend.app.celery_app.celery_app worker -n worker_io -Q q_io,q_default -l info --concurrency=4 -E

  worker_editor:
    <<: *worker-base
    container_name: kombajn_worker_editor
    command: celery -A backend.app.celery_app.celery_app worker -n worker_editor -Q q_cpu_edit -l info --concurrency=1 --prefetch-multiplier=1 -E

  flower:
    <<: *worker-base
    container_name: kombajn_flower
    restart: always
    command: >
      celery
      --app=backend.app.celery_app.celery_app
      flower
      --port=5555
      --inspect-timeout=3000
    ports:
      - "5555:5555"
    environment:
      - KOMBAJN_REDIS_BROKER_URL=redis://redis:6379/0
      - KOMBAJN_REDIS_RESULT_BACKEND=redis://redis:6379/1
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
      - PYTHONPATH=.
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    container_name: kombajn_redis
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: kombajn_redis_commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis-data:
