# KOMBAJN AI – Development Roadmap & TODO
(Updated: 2026-04-23 12:25:00)

## ✅ 1. Infrastructure & Architecture Refactor (Done)
- [x] **Universal AI Services**: Abstract providers for Gemini, Imagen, and Mock.
- [x] **Domain Schemas**: Pydantic models with "one class per file" rule.
- [x] **ColorBook Engine**: Object-oriented processors for PDF/Excel generation.
- [x] **Modular Tasks**: Celery tasks split by domain (video, color_book, system).
- [x] **Dual Docker Profiles**: CPU and GPU specific compose files synchronized.

## 🚀 2. AI Enhancements
- [ ] **Local LLM Provider**: Implement Ollama/Llama integration in `AIServiceFactory`.
- [ ] **Local ImageGen Provider**: Implement Stable Diffusion (ComfyUI API) integration.
- [ ] **Video AI Integration**: Connect `ImageElement.prompt` to the new `ImageGenProvider`.
- [ ] **Voice/TTS Refactor**: Move Voice generation to `backend/app/services/ai/providers/tts.py`.

## 📚 3. ColorBook Studio (Next Steps)
- [ ] **Task Monitoring UI**: Real-time progress tracking in Streamlit (using Celery AsyncResult).
- [ ] **Project Gallery**: View generated manuscripts and covers directly in UI.
- [ ] **Advanced Binding**: Add page numbering, copyright pages, and custom fonts selection.
- [ ] **Line Extraction Preview**: Interactive threshold adjustment for `LineExtractionProcessor`.

## 🎬 4. Video Engine (J2V)
- [ ] **GPU Fast-Path**: Implement FFmpeg/CUDA filters for scaling and composition.
- [ ] **Interactive Preview**: Frame-by-frame preview in Streamlit using MoviePy/OpenCV.
- [ ] **Component Library**: Implement animated components (transitions, lower thirds).

## 🛡️ 5. Quality & Resilience
- [ ] **E2E Testing**: Add full flow tests (API -> Worker -> SSD Output) for both domains.
- [ ] **Cache Management**: Implement automatic cleanup for `/data/ssd/cache`.
- [ ] **Pre-flight Checks**: Validate assets existence and text lengths before starting heavy renders.
