# KOMBAJN AI (The Visual Foundry) - Project Blueprint

## 1. Vision & Goals
**KOMBAJN AI** is a modular, asynchronous multimodal content factory. It automates video production (Shorts, Music Videos, Canvas) based on AI-generated music or stock assets.

**Business Strategy:**
1.  **Original Creation**: Visuals for own music (royalties).
2.  **AI Agency**: Servicing Fiverr/OLX orders (e.g., Shorts/Quiz packs) - **Initial Priority**.
3.  **SaaS**: Providing the platform to end-users.

---

## 2. Technical Architecture
The system follows **Hexagonal Architecture** and is **Event-Driven**.

*   **Compute Factory**: Tasks are mapped to providers (Local GPU, CPU, RunPod, API) via **Pydantic v2** contracts.
*   **Competing Consumers (Pull-Based)**: Celery + Redis. Workers pull tasks based on available resources (`PREFETCH_COUNT=1`).
*   **Atomic Tasks**: Every operation (1 image download, 1 frame analysis) is a separate task. No monolithic tasks.
*   **JSON Manifest Orchestration**: Separation of editing logic (EDL) from the rendering engine.
*   **Tiered Storage**: **fsspec** abstraction for SSD (Active), USB 3.0 (Assets/Models), and HDD (Vault).

---

## 3. Key Logic Mechanisms
*   **Audio De-unification**: Stem separation (Demucs) and Beat Map generation.
*   **Intelligent Vision Attention (Saliency)**:
    *   **Recursive Zoom**: Global scan followed by high-res crops of interesting areas.
    *   **Heuristic Filtering**: Using fast detectors (YOLO) or variance analysis to skip "boring" regions (e.g., empty sky) before invoking heavy VLM models (Moondream2).
    *   **Dynamic Prompting**: Asking the VLM if a crop is "meaningful" before performing deep analysis.
*   **Semantic Decider**: Weighting vision descriptions against project "Interest Profiles" using small LLMs.
*   **Pre-flight Guard**: Resource/dependency check decorator.
*   **Self-Healing Workflow**: Deciders choosing recovery plans (e.g., fallback assets).

---

## 4. Hardware Optimization (GTX 1050 Ti 4GB VRAM)
*   **Sequential Loading**: One heavy model in VRAM at a time + mandatory `torch.cuda.empty_cache()`.
*   **CPU/RAM Offloading**: Vision (Moondream2) on GPU (4-bit), Logic (Llama-3/Phi-3) on CPU (GGUF).
*   **Asset Normalization**: Scaling images to native model resolution before analysis.

---

## 5. Tech Stack
- **Backend**: Python 3.10+, FastAPI, Celery + Redis.
- **UI**: Streamlit (Dynamic forms).
- **Models**: Demucs, Moondream2, Llama-3/Phi-3, YOLOv10.
- **Monitoring**: Flower, Dozzle.

---

## 6. Roadmap
**Sprint 0 (Foundation)**: Docker setup, StorageManager, Atomic Video Orchestration (Tracer Bullet).
**Sprint 1 (Audio)**: De-unification pipeline and `AudioAnalysis.json` generation.
**Sprint 2 (Vision)**: Intelligent Attention Worker (YOLO + Moondream) with Recursive Zoom logic.
**Sprint 3 (Logic & Render)**: Semantic Decider, EDL Generator, MoviePy Engine.
**Sprint 4 (Agency Ready)**: Automated Shorts production with watermarks and multi-format support.

---

## 7. Backlog / Refinements
- DAG-based complex orchestration logic.
- Video-LLM model selection for `by_clips` strategy.
- Automated task priority escalation.
- Hybrid cloud/local sync over LTE hotspot.
