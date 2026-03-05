# Vision Logic & Attention Management Strategy

## Problem: Redundancy in Naive Sliding Window
Processing every frame or every window of an image through a heavy Vision Language Model (VLM) like **Moondream2** is computationally expensive and redundant. For many scenes (e.g., skies, plain backgrounds), the model provides low-value information ("it's a blue sky").

## Solution: Hierarchical & Intelligent Attention
KOMBAJN AI manages attention through a multi-stage orchestration script, ensuring heavy VLM compute is only spent on "interesting" regions.

---

## 1. Stage: Global Scan (Fast Detector)
- **Actor**: `worker.vision_scan`
- **Action**: Use a fast, specialized object detector like **YOLOv8/v10** or simple **Variance Analysis** (edge detection).
- **Goal**: Identify bounding boxes (ROIs - Regions of Interest) where "things" (people, cars, animals, distinct textures) exist.

## 2. Stage: Heuristic Filtering (Saliency Check)
- **Actor**: `worker.vision_filter`
- **Logic**: 
    - If a window's variance is below a certain threshold (flat color), mark it as "Background" and skip deep analysis.
    - If no YOLO objects are detected, classify as "Low Interest" and provide a generic, cached description (e.g., "sky", "grass").

## 3. Stage: Recursive Zoom (Targeted VLM Analysis)
- **Actor**: `worker.vision_describe` (Moondream2)
- **Mechanism**:
    1.  **Crop Extraction**: Take high-resolution crops based on the ROIs identified in Stage 1.
    2.  **Targeted Prompting**: Instead of "What's in this image?", ask Moondream specific questions: *"Describe the clothing of the person in this box"* or *"What is the interaction between these two identified objects?"*.
    3.  **Recursive Depth**: If a crop still contains a dense cluster, recurse another level (zoom in further) to resolve individual elements.

## 4. Stage: Semantic Filtering & Fusion
- **Actor**: `orchestrator.vision_summarize` (Small LLM)
- **Action**: 
    - Fuse individual window/crop descriptions into a coherent scene graph.
    - Filter out redundant descriptions (e.g., "blue sky" mentioned in 20 windows).
    - Map descriptions to the project's **Interest Profile** (e.g., if the project is about "birds," prioritize avian-related descriptions).

---

## Technical Pipeline (Sprint 2)
1.  **Image Input** -> 1080p source.
2.  **YOLO Scan** -> List of Bounding Boxes (e.g., `person [x,y,w,h]`).
3.  **Crop Selection** -> Focus windows around high-density BBox areas.
4.  **Moondream Call** -> Perform VLM analysis only on selected crops.
5.  **JSON Metadata** -> Save to SQLite: `{frame_id, ROI, description, saliency_score}`.

## Advantages
- **Performance**: Up to 80% reduction in VLM calls.
- **Precision**: Higher resolution "zoomed" inputs lead to better OCR and detail recognition.
- **Context**: The orchestrator maintains global awareness while the VLM handles local details.
