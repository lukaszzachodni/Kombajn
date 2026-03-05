# KOMBAJN AI (The Visual Foundry)

**KOMBAJN AI** is a modular, asynchronous, and multimodal AI content factory. It automates the production of high-quality visual content (Shorts, Music Videos, Canvas) driven by AI-generated music and stock assets.

Built on an **Atomic-Task Architecture**, the system decomposes complex workflows into small, independent, and parallelizable processing units ("Atoms") managed by a robust Celery queue.

---

## 🚀 Core Architecture
- **JSON Manifest-Driven**: Everything is declarative. A single JSON file defines the entire edit, logic, or analysis pipeline.
- **Event-Driven & Atomic**: High-level requests are broken down into hundreds of tiny tasks (e.g., `render_scene`, `analyze_beat`, `detect_roi`).
- **Compute Factory**: Agnostic hardware mapping allows tasks to run locally (GTX 1050 Ti) or on cloud GPU clusters (RunPod/S3).
- **Single Source of Truth (SSOT)**: Pydantic v2 schemas strictly validate all data flows across API, Worker, and UI.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.10+, FastAPI, Celery + Redis.
- **Processing**: MoviePy (Video), Demucs (Audio), Moondream2 (Vision), YOLOv10 (Detection).
- **UI**: Streamlit (Operational Control Panel).
- **Monitoring**: Flower (Real-time Queue Monitoring).
- **Infrastructure**: Docker Compose (Multi-container stack).

---

## 📦 Installation & Setup

### Prerequisites
- [Docker](https://www.docker.com/get-started) & Docker Compose.
- (Optional) NVIDIA Docker Runtime (for GPU acceleration).

### Quick Start
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lukaszzachodni/Kombajn.git
    cd kombajn
    ```
2.  **Build and Start the Stack**:
    ```bash
    docker-compose build
    docker-compose up -d
    ```

---

## ⚙️ Operational Guide

Once the stack is up, you can access the following dashboards:

| Service | Local URL | Description |
| :--- | :--- | :--- |
| **API Docs** | `http://localhost:8000/docs` | Swagger/OpenAPI interactive testing. |
| **Control Panel** | `http://localhost:8501` | Streamlit UI for launching renders. |
| **Flower** | `http://localhost:5555` | Real-time task & worker monitoring. |
| **Landing Page**| `http://localhost:8000` | Static startup panel and health status. |

---

## 🏗️ Project Structure
- `backend/app/`: Core logic, Celery tasks, and Pydantic schemas.
- `backend/streamlit_app.py`: Operations UI.
- `docs/architecture/`: Deep-dive architectural documentation.
- `data/`: Tiered storage mounts (SSD/HDD/USB).

---

## ⚖️ License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---
*Sprint 0 · Infrastructure & Atomic Video Foundation*
