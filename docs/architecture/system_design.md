# System Design: KOMBAJN AI

## Overview
KOMBAJN AI is a modular video rendering engine based on Pydantic v2 schemas and MoviePy.

## Domain Definitions & Flow

### Key Concepts
- **Template**: The "Blueprint". Describes the montage logic, timing (chronology), and spatial layout of elements. It defines *how* the movie is assembled, but *not* the content (Assets).
- **Assets**: Raw media (images, audio, video, text) used to fulfill the template requirements.
- **Project**: The end-to-end client engagement encompassing the Template, specific Assets, and final generated Outputs.
- **Manifest**: The concrete, final JSON produced after injecting Assets into a Template. It contains resolved paths, specific data, and is ready for the Worker.
- **Queue (Job)**: The processing channel (e.g., `q_cpu_edit`) where tasks are dispatched.
- **Task**: The atomic unit of work (rendering one Manifest) processed by a Worker.
- **Output (Render)**: The final `.mp4` file produced by a Worker after executing a Task.

### Processing Flow
1. **Definition**: You design the **Template** (spatial/temporal montage logic).
2. **Configuration**: You create a **Project** by selecting a Template and providing the specific **Assets** (content).
3. **Orchestration**: The system compiles a **Manifest** (the ready-to-render JSON).
4. **Execution**: The Manifest is dispatched as a **Task** to a **Queue**.
5. **Production**: A **Worker** processes the Task and produces the final **Output**.

## Modular Structure
The codebase is modularized:
- `backend/app/engine/elements/`: Pydantic models for elements.
- `backend/app/engine/processors/`: MoviePy rendering logic.
- `backend/app/engine/j2v_types.py`: Unified registry (`J2VAnyElement`).
- `backend/app/api/`: Modular FastAPI endpoints.

## Testing Standards
- All J2V manifest tests must use JSON files stored in `backend/app/tests/manifests/`.
- Integration tests verify the flow: `Manifest JSON` -> `Pydantic` -> `Renderer` -> `MoviePy Output`.
