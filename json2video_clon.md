# JSON2Video Local Clone - Implementation Plan

## Vision
To provide a local, open-source alternative to the json2video.com API, allowing users to render videos using the same JSON manifest syntax but running on local hardware (MoviePy, FFMPEG, local AI models).

## Architectural Guidelines
- **OOP First**: Always use Classes and Methods. Procedural "scripting" style is forbidden.
- **SOLID Principles**:
    - **SRP**: Processors only handle rendering, Renderer only handles orchestration.
    - **OCP**: Adding a new element type only requires a new class and factory registration.
- **Factory Pattern**: Centralized `J2VProcessorFactory` for mapping types to logic.
- **Robust Compositing**: Custom frame-by-frame compositor to bypass MoviePy/Numpy broadcasting bugs.

## Iteration 1: Core Schema & Common Properties
- [x] Define base `Movie` and `Scene` schemas (Pydantic v2).
- [x] Implement common properties: `start`, `duration`, `fade-in/out`, `z-index`.
- [x] Handle evaluated expressions and variables.

## Iteration 2: Static Elements (Image & Text)
- [x] `J2VImageProcessor`: support for `src`, `resize: cover/fit`, positioning.
- [x] `J2VTextProcessor`: robust masking strategy to avoid Numpy errors, support for `settings` (CSS).

## Iteration 3: Multimedia Elements (Video & Audio)
- [x] `J2VVideoProcessor`: `seek`, `volume`, `muted`, `loop`, `flip`.
- [x] `J2VAudioProcessor`: background music handling with safe sub-clipping.

## Iteration 4: Dynamic & AI Elements
- [x] `J2VVoiceProcessor`: Local TTS integration (gTTS).
- [x] `J2VAudiogramProcessor`: Basic placeholder (ready for Librosa implementation).
- [x] `J2VSubtitlesProcessor`: Basic placeholder (ready for Whisper implementation).

## Iteration 5: Advanced Logic
- [x] Conditional elements (`condition` property).
- [x] Loops and iterations (`iterate` property).
- [ ] Caching system implementation (Pending).

---
*Status: Iteration 5 completed (Logic) - Engine is fully operational for dynamic projects.*
