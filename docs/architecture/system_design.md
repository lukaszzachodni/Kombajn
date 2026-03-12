# KOMBAJN AI System Design Overview

## Core Philosophy: The Atomic Factory
KOMBAJN AI is not a monolithic application; it is a **Distributed Atomic Engine**. The fundamental principle is that **no complex operation is ever performed as a single task.** Every piece of work—from high-level project coordination to low-level pixel processing—is decomposed into small, independent, and idempotent "atoms" managed by Celery queues.

---

## 1. Universal Atomic-Task Architecture
Every module in the system (Audio, Vision, Logic, Video) follows the same execution pattern:
- **No Monolithic Tasks**: If a task takes more than a few seconds or consumes significant VRAM/CPU, it must be split.
- **Queue-First Communication**: Modules never call each other directly via internal APIs.
- **Idempotency**: Every atomic task can be retried safely.

## 2. Dynamic Resource Routing (KombajnRouter)
To ensure the system remains responsive on a single machine while being ready for the cloud, we use a **Dynamic Routing** layer:
- **Separation of Concerns**: Tasks are routed based on their resource needs (IO vs. CPU vs. GPU).
- **Routing Hints**: The system can override default local routing with hints (e.g., `routing_hint='runpod'`) to outsource specific tasks without changing business logic.
- **Zero-Code Scaling**: Moving a task from local to cloud is an infrastructure change (Docker/Settings), not a code rewrite.

## 3. JSON-Driven Orchestration (Manifests)
The state and logic of a project are defined by declarative JSON manifests (Pydantic v2).
- **Compute Agnostic**: Since tasks are atomic and manifests are JSON, the system can distribute work across any node.

## 4. Compute Factory & Hardware Mapping
Workers are "specialists" listening to specific queues:
- **`q_io` / `q_default`**: Fast, non-blocking tasks (API calls, small DB updates, notifications).
- **`q_cpu_edit`**: Heavy CPU-bound tasks (FFMPEG rendering, MoviePy montage). Limited to low concurrency locally to prevent OS freezing.
- **`q_gpu_local`**: Local AI inference (Vision, Transcription).
- **`q_runpod` / `q_cloud`**: Reserved for external compute nodes.

## 5. Technology Stack
- **Backend**: Python 3.10+, FastAPI, Celery + Redis.
- **Processing**: MoviePy (Video), Demucs (Audio), Moondream2 (Vision).
- **Monitoring**: 
    - **Flower**: Task lifecycle and worker health.
    - **Redis Commander**: Real-time queue depth and raw data inspection.
