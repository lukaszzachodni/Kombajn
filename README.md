# KOMBAJN AI – The Visual Foundry

Modular video production engine based on Pydantic v2 schemas and MoviePy. Designed for scalable, template-driven video creation.

## Domain Dictionary
- **Template**: Base JSON with montage logic (no content/assets).
- **Assets**: Media files (images, audio, video, text) used to populate a template.
- **Manifest**: Filled template with specific paths/data (ready for rendering).
- **Project**: Client engagement containing the Manifest and associated Output.
- **Job (Queue)**: Processing channel (e.g., `q_cpu_edit`).
- **Task**: Atomic rendering unit processed by a worker.
- **Output (Render)**: Final MP4 file.

## Architecture
- `backend/app/engine/elements/`: Pydantic models for montage elements.
- `backend/app/engine/processors/`: MoviePy logic per element type.
- `backend/app/api/`: Modular FastAPI endpoints.
- `backend/app/modules/color_book/`: External coloring book generator & binding logic.

## Color Book Module
This module handles coloring book idea generation, image generation, and PDF binding.
- **Idea Generation**: `POST /color-book/idea` - Generates project structure from a theme.
- **Generator**: `backend/app/modules/color_book/generator/`
- **Binding**: `backend/app/modules/color_book/binding/` (PDF & Excel generation)

## Operational Stack
- **API**: `:8000` (FastAPI + Swagger docs)
- **Studio (Composer)**: `:8501` (Streamlit Studio)
- **Monitoring**: `:5555` (Flower) / `:8081` (Redis Commander)

## Quick Start & Deployment

### Hardware Agnostic Setup
Kombajn AI supports both CPU (any machine) and NVIDIA GPU (Xubuntu with NVIDIA drivers) rendering.

#### 1. For CPU-only rendering (Windows/Intel or Cloud)
Use the CPU-optimized configuration:
```bash
docker compose -f docker-compose.cpu.yml up -d --build
```

#### 2. For NVIDIA GPU rendering (Xubuntu)
Ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed on your host, then run:
```bash
docker compose -f docker-compose.gpu.yml up -d --build
```

*Note: The GPU-optimized configuration will fall back to CPU rendering if it fails to find an available NVIDIA driver/adapter.*
