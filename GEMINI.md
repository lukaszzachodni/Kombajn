# KOMBAJN AI – Coding Standards & Mandates

## Communication Protocols
- **Timestamping**: Zawsze podawaj aktualną datę i czas (YYYY-MM-DD HH:MM:SS) na początku każdej swojej wypowiedzi.
- **Task-Driven**: Operate as an autonomous executor. Do not suggest next steps, ask if you should proceed, or inquire about user intent. If you have finished a task, wait for the next Directive.
- **Precision**: If a request is ambiguous, ask for technical clarification only.
- **Focus & Atomicity**: Zajmujemy się tylko jedną funkcjonalnością lub błędem naraz. Nie wprowadzaj zmian "przy okazji" (np. poprawki frontendu przy naprawie backendu), chyba że zostaniesz o to wyraźnie poproszony. Każda zmiana musi być ściśle ograniczona do zgłoszonego problemu.
- **No Filler**: Remove all conversational filler, empathetic postambles, and conversational "check-ins."
- **Assumption-Free**: Do not assume a task is complete, functional, or that the user is satisfied. Report results concisely and wait.

## 🏗️ Architecture & Style
- **OOP First**: Always use Classes and Methods. Procedural "scripting" style is forbidden for core logic.
- **SOLID Principles**:
    - **Single Responsibility (SRP)**: Each class must have one reason to change. Separate "what to do" from "how to render".
    - **Open/Closed (OCP)**: Adding a new element type must only require adding a new class and registering it in a factory.
    - **Interface Segregation**: Prefer small, focused interfaces over monolithic ones.
- **No If-Chains**: Factory Pattern or Registry Pattern must be used instead of `if type == "text": ... elif type == "image": ...`.
- **Modular File Structure**: 
    - Business logic in `backend/app/engine/`.
    - API endpoints separated into modules in `backend/app/api/`.
    - Data structures in `backend/app/engine/elements/`.

## 🚀 Strategic Roadmap & ROI (Post-Template Production)
- **High-Performance "Fast-Path"**: Po wdrożeniu masowej produkcji z szablonów, priorytetem jest implementacja `J2VGPUAccelerator`.
- **GPU-Centric Orchestration**: Przeniesienie operacji skalowania, mozaiki i dekodowania z MoviePy (CPU) bezpośrednio do filtrów FFmpeg/CUDA (GPU).
- **Hybrid Rendering Model**:
    - **Simple/Heavy Scenes** (wideo, tła, mozaiki): Direct FFmpeg/CUDA (ROI: 5-10x speedup).
    - **Complex/Creative Scenes** (dynamiczne napisy, filtry artystyczne): MoviePy/CPU.
- **Goal**: Umożliwienie masowej produkcji wideo 4K/60fps na maszynach o słabszym CPU (np. pod zlecenia Fiverr) przy 100% wykorzystaniu enkodera NVENC/HEVC.

## 🛡️ Resilience & Atomicity Mandates
- **Task Granularity**: Każdy render musi być rozbity na najmniejsze możliwe jednostki (sceny). Długie sceny (powyżej 5 min) powinny być dzielone na pod-zadania.
- **Stateless Intermediate Storage**: Pliki tymczasowe scen muszą być traktowane jako checkpointy. W razie awarii, system musi umożliwiać wznowienie renderu od brakującej sceny bez powtarzania gotowych fragmentów.
- **Fail-Fast**: Błąd w jednej scenie nie może blokować zasobów całego klastra; musi być raportowany natychmiast, umożliwiając poprawkę manifestu i "hot-retry".

## 🎥 Rendering Standards
- **Atomicity**: Rendering a single scene is an atomic unit of work.
- **Stability**: Always convert clips to RGB/RGBA and use explicit sizes.
- **Cleanup**: Every processor is responsible for closing its clips and freeing resources.

## 🛠️ Operational Commands
- **Docker-First Execution**: Wszystkie komendy, skrypty oraz testy muszą być uruchamiane wewnątrz kontenerów Docker (np. przez `docker compose exec`). Nie uruchamiaj logiki biznesowej bezpośrednio na host'cie, aby uniknąć problemów z brakującymi zależnościami (np. numpy, moviepy).
- Use `docker compose` (not `docker-compose`).
- Verify routing with `smoke_test_routing.py`.

## 💻 Production Environment (Host Hardware)
- **CPU**: Intel Core i5-3470 (4 cores, 4 threads)
- **RAM**: 24GB DDR3
- **GPU**: NVIDIA GeForce GTX 1050 Ti (4GB VRAM)
- **Storage**: SSD (SATA3)
- **OS Context**: Linux with NVIDIA Container Runtime enabled.

