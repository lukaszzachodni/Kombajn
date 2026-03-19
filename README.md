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

## Operational Stack
- **API**: `:8000` (FastAPI + Swagger docs)
- **Studio (Composer)**: `:8501` (Streamlit Studio)
- **Monitoring**: `:5555` (Flower) / `:8081` (Redis Commander)

## Quick Start
```bash
docker compose up -d --build
```
Access the dashboard at `http://localhost:8000`.
