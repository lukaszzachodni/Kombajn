# Video Orchestration Flow (KOMBAJN AI)

## Overview
The video rendering pipeline in KOMBAJN AI follows an **Atomic-Task Architecture** with a **Fan-Out/Fan-In (Chord)** pattern. This ensures horizontal scalability (multiple workers rendering scenes in parallel) and resource optimization.

---

## 1. Stage: Validation & Pre-flight
- **Actor**: API (FastAPI)
- **Action**: Validate manifest and check assets existence.
- **Success Criteria**: Dispatched to `orchestrate_video_render`.

## 2. Stage: Fan-Out (Decomposition)
- **Actor**: Orchestrator (Celery Task)
- **Logic**: Parses manifest into `Scene` objects and creates a **Celery Chord**.
- **Routing**: Header tasks are routed via `KombajnRouter`.

## 3. Stage: Atomic Rendering (Parallel Processing)
- **Actor**: `worker_editor` (Listening to `q_cpu_edit`)
- **Action**:
    - **MoviePy** creates composite clips.
    - Each scene rendered as high-bitrate `.mp4` intermediate.
- **Local Optimization**: Locally, `worker_editor` runs with `concurrency=1` to ensure the host OS remains responsive during heavy FFMPEG processes.

## 4. Stage: Synchronization & Fan-In
- **Actor**: Celery Broker (Redis)
- **Action**: Monitors `SUCCESS` status for all scene tasks. Once complete, triggers the callback.

## 5. Stage: Assembly (Stitching)
- **Actor**: `worker_editor` (Listening to `q_cpu_edit`)
- **Action**: Concatenates all intermediate files in order into the final video file.

## 6. Stage: Post-processing & Cleanup
- **Actor**: Worker / Orchestrator
- **Action**: Moves final file to `/data/ssd/renders/{project_id}/` and clears the `temp/` directory.

---

## Hardware Isolation Strategy
- **IO Worker**: Handles all non-heavy tasks (metadata, API calls) in `q_io` and `q_default`.
- **Editor Worker**: Dedicated to `q_cpu_edit` (FFMPEG). By isolating it, we can scale it independently (e.g., move only this worker to a cloud node if local CPU is too slow).
