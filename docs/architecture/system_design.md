# System Design: KOMBAJN AI

## Overview
KOMBAJN AI is a modular video rendering engine based on Pydantic v2 schemas and MoviePy, simulating JSON2Video manifest logic.

## Recent Architectural Changes (March 2026)
- **Manifest-as-Code**: Projects are stored as `.json` files in `/data/projects` to enable Git-based versioning and syncing between environments.
- **Dynamic Frontend Composer**: Built on top of Streamlit, dynamically generates forms from Pydantic models using a custom `ui_builder.py` module.
- **Asset Management**: 
    - Dedicated storage in `/data/assets/{images, videos, audio, fonts}`.
    - Automatic deduplication using MD5 file hashing.
    - Integrated Asset Picker in the UI with file upload capabilities.
- **Improved Data Integrity**: Discriminated unions (`J2VAnyElement`) used for polymorphic elements in the Pydantic models, enabling strict validation and full OpenAPI documentation coverage.

## Key Modules
- `backend/app/engine/j2v_types.py`: The "Source of Truth". Contains all data models and union definitions.
- `backend/app/engine/asset_manager.py`: Handles asset storage and file system interactions.
- `backend/app/engine/project_store.py`: Persistent storage for project manifests.
- `backend/app/engine/ui_builder.py`: Maps Pydantic schemas to Streamlit widgets with field prioritization and nested UI handling.

## Known Limitations / TODOs
- **Circular Imports**: Managed via `TYPE_CHECKING` and `model_rebuild()` due to Pydantic/OpenAPI requirements for complex unions.
- **Performance**: Heavy AI image generation and rendering processes are offloaded to Celery workers (`worker_io`, `worker_editor`).
- **UI UX**: "Expert Mode" in Composer allows manual JSON editing for advanced manifest features not yet supported by the dynamic form.
