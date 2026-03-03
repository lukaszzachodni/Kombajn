Oto szczegółowe podsumowanie wszystkich ustaleń projektowych dla systemu **KOMBAJN AI (The Visual Foundry)**, przygotowane jako gotowy dokument bazowy.

### 1. Wizja i Cele Projektu
**KOMBAJN AI** to modularna, asynchroniczna fabryka treści multimodalnych. System służy do zautomatyzowanej produkcji wideo (Shorts, teledyski, Spotify Canvas) na podstawie muzyki generowanej przez AI lub zasobów stockowych.

**Strategia biznesowa (3 Kręgi):**
1.  **Własna Twórczość:** Produkcja wizuali dla własnej muzyki na streamingi (tantiemy).
2.  **Agencja AI:** Obsługa zleceń na Fiverr/OLX, np. paczki shortsów/quizów (priorytet na start).
3.  **SaaS:** Udostępnienie platformy użytkownikom końcowym.

---

### 2. Architektura Techniczna (Fundamenty)
System opiera się na **Architekturze Heksagonalnej (Ports & Adapters)** oraz przetwarzaniu **sterowanym zdarzeniami (Event-Driven)**.

*   **Agnostycyzm Obliczeniowy (Compute Factory):** Warstwa pośrednia mapuje zadania na dostawców (lokalne GPU, CPU, RunPod, API). Wybór dostawcy jest przeźroczysty dla logiki biznesowej dzięki kontraktom **Pydantic v2**.
*   **Model Pull-Based (Competing Consumers):** Wykorzystanie **Celery i Redis**. Workery same pobierają zadania z kolejki, gdy mają wolne zasoby (`PREFETCH_COUNT=1`), co chroni słabszy sprzęt przed przeciążeniem.
*   **Zadania Atomowe (Atomic Tasks):** Każda operacja (pobranie 1 zdjęcia, analiza 1 klatki) to osobne zadanie. Zakaz stosowania zadań monolitycznych.
*   **Orkiestracja przez JSON Manifests:** Rozdzielenie logiki edycji (EDL - Edit Decision List) od silnika renderującego (Dumb Renderer).
*   **Tiered Storage Strategy:** Wykorzystanie biblioteki **fsspec** do abstrakcji systemu plików.
    *   **SSD (Active):** system, Docker, baza SQLite, renderowanie w `/tmp`.
    *   **USB 3.0 (Assets):** surowe materiały stockowe, wagi modeli AI (szybki odczyt).
    *   **HDD (Vault):** gotowe rendery, logi, backupy.

---

### 3. Kluczowe Mechanizmy Logiki
*   **Desunifikacja Audio:** Rekonstrukcja „sklejonych” piosenek z AI na stemy (perkusja, wokal, bas) i generowanie map rytmicznych (**Beat Map**).
*   **Sliding Window Saliency:** Analiza obrazu na gęstej siatce z nakładaniem się pól (np. 50% overlap). Eliminuje to „martwe strefy” i pozwala na płynny ruch kamery w kierunku punktów zainteresowania (ROI).
*   **Semantic Decider:** Ważenie opisów wizyjnych na podstawie „Profilu Zainteresowań” projektu (np. szukaj ptaków, ignoruj ludzi) przy użyciu małych modeli LLM lub NLP.
*   **Pre-flight Guard:** Dekorator sprawdzający zależności i zasoby przed startem zadania (np. czy pliki istnieją, czy VRAM jest dostępny).
*   **Self-Healing Workflow:** Mechanizm „Decyderów” dobierający plan naprawczy w razie błędu (np. pobierz inne zdjęcie, jeśli stock API zwróci błąd).

---

### 4. Optymalizacja Sprzętowa (GTX 1050 Ti 4GB VRAM)
System jest skrajnie zoptymalizowany pod kątem niskich zasobów:
*   **Sequential Loading:** Ładowanie tylko jednego ciężkiego modelu AI do VRAM naraz i obowiązkowe czyszczenie cache (`torch.cuda.empty_cache()`) między seriami zadań.
*   **CPU/RAM Offloading:** Modele wizyjne (Moondream2) działają na GPU (4-bit NF4), a modele logiczne (Llama-3/Phi-3) na CPU, wykorzystując 24GB RAM systemowego (format GGUF).
*   **Asset Normalization:** Skalowanie obrazów do natywnej rozdzielczości modelu przed analizą GPU.
*   **Project-Locked Workflow:** Opcjonalne skupienie workera na jednym projekcie do momentu jego ukończenia, aby uniknąć częstego przeładowywania modeli.

---

### 5. Tech Stack i Tooling
*   **Backend:** Python 3.10+, FastAPI, Celery + Redis (AOF Persistence).
*   **UI:** Streamlit (generowany dynamicznie ze schematów Pydantic).
*   **Modele:** Demucs (audio), Moondream2 (vision), Llama-3/Phi-3 (logic).
*   **Narzędzia dev:** Cursor (IDE), Flower (kolejki), Dozzle (logi), DBeaver (SQLite).
*   **Standardy:** JSON Schema, CloudEvents, Git (z rygorystycznym `.gitignore` dla modeli i assetów).

---

### 6. Mapa drogowa i priorytety (Trello)
**Sprint 0 (Fundamenty):** Setup Dockera (GPU passthrough), `StorageManager` (fsspec), bazowe modele Pydantic i „Tracer Bullet” (klip 5s z jednym zoomem).
**Sprint 1 (Audio):** Pipeline desunifikacji (Demucs) i generowanie `AudioAnalysis.json`.
**Sprint 2 (Vision):** Worker Moondream2 z algorytmem Sliding Window i zapisem metadanych w SQLite.
**Sprint 3 (Logic & Render):** Semantic Decider, generator EDL i „głupi” silnik renderujący MoviePy.
**Sprint 4 (Agency Ready):** Produkcja shortsów na Fiverr (automatyczne znaki wodne, multiformat: 16:9, 9:16, Canvas).

---

### 7. Rzeczy do doprecyzowania (Backlog)
*   Szczegółowa logika orkiestracji złożonych scenariuszy (DAG).
*   Wybór konkretnego modelu Video-LLM dla strategii `by_clips`.
*   Automatyczne podbijanie priorytetu zadań „wiszących” zbyt długo w kolejce.
*   Ostateczna konfiguracja wysyłania/pobierania danych przy pracy hybrydowej (lokalnie vs chmura) przez hotspot LTE.