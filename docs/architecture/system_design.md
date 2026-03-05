# KOMBAJN AI System Design Overview

## Core Philosophy: The Atomic Factory
KOMBAJN AI is not a monolithic application; it is a **Distributed Atomic Engine**. The fundamental principle is that **no complex operation is ever performed as a single task.** Every piece of work—from high-level project coordination to low-level pixel processing—is decomposed into small, independent, and idempotent "atoms" managed by Celery queues.

---

## 1. Universal Atomic-Task Architecture
Every module in the system (Audio, Vision, Logic, Video) follows the same execution pattern:
- **No Monolithic Tasks**: If a task takes more than a few seconds or consumes significant VRAM/CPU, it must be split.
- **Queue-First Communication**: Modules never call each other directly via internal APIs. They "talk" by placing atomic tasks into specific queues (`audio_processing`, `vision_analysis`, `video_rendering`).
- **Idempotency**: Every atomic task can be retried safely. If a worker crashes while rendering 1 second of video or analyzing 5 seconds of audio, only that atom is re-executed.

## 2. JSON-Driven Orchestration (Manifests)
The state and logic of a project are defined by declarative JSON manifests.
- **Single Source of Truth**: Pydantic v2 models define exactly what is possible.
- **Workflow as Data**: A "project" is just a series of manifests that transition through different atomic states.
- **Compute Agnostic**: Since tasks are atomic and manifests are JSON, the system can distribute work across a local GPU, a remote CPU cluster, or a cloud API without changing a single line of business logic.

## 3. Module Examples as Atomic Flows
- **Audio Module**: Instead of "Process Song," it triggers `split_stems` (Demucs), then multiple `analyze_rhythm` tasks for each stem, then `generate_beatmap`.
- **Vision Module**: Instead of "Analyze Video," it triggers hundreds of `detect_roi` and `describe_frame` tasks in parallel.
- **Video Module**: Already implemented as `render_scene` atoms followed by an `assemble_video` stitcher.

## 4. Compute Factory & Hardware Mapping
- **Resource-Aware Routing**: Workers are "specialists." A worker with 4GB VRAM only takes `render_scene` or `vision_analysis` atoms. A CPU worker takes `logic` or `assembly` atoms.
- **Tiered Storage**: `fsspec` abstracts all file operations, allowing atomic tasks to read/write to SSD, HDD, or S3 seamlessly.
- **Horizontal Scaling**: Adding more "compute nodes" (containers) immediately speeds up the entire factory by increasing the throughput of atomic processing.

---

## 5. Technology Stack
- **Backend**: Python 3.10+, FastAPI, Celery + Redis (Orchestration).
- **Processing**: MoviePy (Video), Demucs (Audio), Moondream2 (Vision).
- **Tooling**: Flower (Queue Monitoring), Pydantic (Contract Validation).
