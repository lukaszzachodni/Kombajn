# KOMBAJN AI – Coding Standards & Mandates

## 🏗️ Architecture & Style
- **OOP First**: Always use Classes and Methods. Procedural "scripting" style is forbidden for core logic.
- **SOLID Principles**:
    - **Single Responsibility (SRP)**: Each class must have one reason to change. Separate "what to do" from "how to render".
    - **Open/Closed (OCP)**: Adding a new element type (e.g., `sticker`) must only require adding a new class and registering it in a factory, NOT modifying existing rendering logic.
    - **Interface Segregation**: Prefer small, focused interfaces over monolithic ones.
- **No If-Chains**: Factory Pattern or Registry Pattern must be used instead of `if type == "text": ... elif type == "image": ...`.
- **Modular File Structure**: 
    - Business logic belongs in `backend/app/engine/`.
    - Celery tasks in `backend/app/tasks.py` are only thin wrappers (entrypoints).
    - Data structures in `backend/app/schemas.py`.

## 🎥 Rendering Standards
- **Atomicity**: Rendering a single scene is an atomic unit of work.
- **Stability**: Always convert clips to RGB/RGBA and use explicit sizes to prevent Numpy/MoviePy broadcasting errors.
- **Cleanup**: Every processor is responsible for closing its clips and freeing resources.

## 🛠️ Operational Commands
- Use `docker compose` (not `docker-compose`).
- Verify routing with `smoke_test_routing.py`.
