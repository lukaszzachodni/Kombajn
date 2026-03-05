# Video Orchestration Flow (KOMBAJN AI)

## Overview
The video rendering pipeline in KOMBAJN AI follows an **Atomic-Task Architecture** with a **Fan-Out/Fan-In (Chord)** pattern. This ensures horizontal scalability (multiple workers rendering scenes in parallel) and resource optimization.

---

## 1. Stage: Validation & Pre-flight
- **Actor**: API (FastAPI)
- **Action**: 
    - Validate incoming JSON against the `VideoEditManifest` Pydantic model.
    - Verify that all referenced assets (images, video files) exist in the `StorageManager` (e.g., in `/data/ssd/assets`).
- **Success Criteria**: A unique `task_id` is returned, and the manifest is dispatched to the orchestrator.

## 2. Stage: Fan-Out (Decomposition)
- **Actor**: Orchestrator (Celery Task)
- **Logic**: 
    - The orchestrator parses the manifest into individual `Scene` objects.
    - It creates a **Celery Chord**:
        - **Header**: A group of `render_scene` tasks (one per scene).
        - **Callback**: A single `assemble_video` task that waits for the header to complete.
- **Data Flow**: The manifest is serialized into scene-level dictionaries to maintain task atomicity.

## 3. Stage: Atomic Rendering (Parallel Processing)
- **Actor**: Worker(s) (Celery Worker)
- **Action**: 
    - Each worker receives a single `Scene` definition.
    - **MoviePy** creates a composite clip (Background + Overlays/Text).
    - The scene is rendered as a high-bitrate, lossless-quality intermediate file (e.g., `scene_001.mp4`).
- **Storage**: Temporary files are stored in `/data/ssd/temp/{project_id}/`.
- **Scaling**: If 10 workers are online, 10 scenes can be rendered simultaneously.

## 4. Stage: Synchronization & Fan-In
- **Actor**: Celery Broker (Redis)
- **Action**: 
    - Monitors the completion status of all scene rendering tasks.
    - If a task fails, Celery handles retries for that specific scene without affecting others.
    - Once all scenes are marked as `SUCCESS`, the list of temporary file paths is passed to the callback.

## 5. Stage: Assembly (Stitching)
- **Actor**: Worker (Celery Worker)
- **Action**: 
    - Loads the list of intermediate scene files in the correct order.
    - Concatenates them into the final video file.
    - Applies final encoding settings (e.g., H.264, target bitrate for Shorts).
- **Audio Integration**: (Upcoming) Merge the beat-map synchronized audio stems.

## 6. Stage: Post-processing & Cleanup
- **Actor**: Worker / Orchestrator
- **Action**: 
    - Move the final file from `temp` to the permanent render path `/data/ssd/renders/{project_id}/`.
    - Delete all intermediate scene files in the `temp` directory.
    - Update the project status in the database to `COMPLETED`.

---

## Storage & Persistence Strategy
- **SSD (Active)**: Used for all `temp/` files and current `renders/`.
- **Abstract Layer**: Using `fsspec` ensures that switching from local storage to S3/RunPod storage will require zero changes to the logic.
- **Persistence**: Task states are tracked via the Redis result backend, but a persistent DB (SQLite) should be introduced for long-running project state management.

## Failure Handling
- **Individual Scene Failure**: Retry the specific `render_scene` task.
- **Orchestrator Failure**: Re-run the validation and decomposition (idempotent).
- **Assembly Failure**: Re-run concatenation from existing temp files (skip rendering).
