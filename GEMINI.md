# KOMBAJN AI – Coding Standards & Mandates

## Communication Protocols
- **Timestamping**: Zawsze podawaj aktualną datę i czas (YYYY-MM-DD HH:MM:SS) na początku każdej swojej wypowiedzi.
- **Task-Driven**: Operate as an autonomous executor. Do not suggest next steps, ask if you should proceed, or inquire about user intent. If you have finished a task, wait for the next Directive.
- **Precision**: If a request is ambiguous, ask for technical clarification only.
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

## 🎥 Rendering Standards
- **Atomicity**: Rendering a single scene is an atomic unit of work.
- **Stability**: Always convert clips to RGB/RGBA and use explicit sizes.
- **Cleanup**: Every processor is responsible for closing its clips and freeing resources.

## 🛠️ Operational Commands
- Use `docker compose` (not `docker-compose`).
- Verify routing with `smoke_test_routing.py`.
