# AI Services & Domain Schemas Refactor (2026-04-23)

## Overview
Celem refaktoryzacji było ujednolicenie narzędzi AI (LLM, Image Generation) dla całej aplikacji oraz uporządkowanie modeli danych (Pydantic) zgodnie z zasadami czystej architektury i obiektowości.

## 1. Universal AI Services (`backend/app/services/ai/`)
Wprowadzono warstwę abstrakcji pozwalającą na przełączanie dostawców AI na poziomie projektu.

- **Abstrakcyjne bazy**: `LLMProvider`, `ImageGenProvider` w `base.py`.
- **Dostawcy Cloud**: `GeminiProvider` (tekst/JSON), `ImagenProvider` (obraz).
- **Dostawca Mock**: `MockLLMProvider`, `MockImageGenProvider` do błyskawicznych testów bez kosztów API.
- **Fabryka**: `AIServiceFactory` dobiera dostawcę na podstawie modelu `AIPreferences`.

## 2. Domain Schemas (`backend/app/schemas/`)
Uporządkowano modele danych, stosując zasadę **jeden plik = jedna klasa**.

- **`common/`**: Wspólne typy hybrydowe (`HInt`, `HFloat`, `HBool`) oraz preferencje AI (`AIPreferences`).
- **`video/`**: Wszystkie elementy J2V (Text, Image, Video, etc.) przeniesione z `engine/elements`.
- **`color_book/`**: Struktura projektu kolorowanki, uploader data KDP, biblioteki promptów.

## 3. Color Book Engine (`backend/app/engine/color_book/`)
Przeniesiono i zhermetyzowano logikę generowania materiałów dla KDP w obiektowych procesorach:
- `ManuscriptProcessor`: Składanie PDF manuskryptu.
- `CoverProcessor`: Składanie PDF okładki (front, grzbiet, tył).
- `KDPExcelProcessor`: Generowanie arkusza uploader'a.
- `LineExtractionProcessor`: Optymalizacja obrazów AI (OpenCV).
- `ColorBookOrchestrator`: Mózg domeny zarządzający przepływem zadań.

## 4. Tasks Orchestration (`backend/app/tasks/`)
Rozbito monolit `tasks.py` na modularne pakiety:
- `tasks/video.py`: Renderowanie wideo J2V (MoviePy/FFmpeg).
- `tasks/color_book.py`: Potok generowania kolorowanek (AI -> Processors).
- `tasks/system.py`: Zadania administracyjne (ping).

## 5. Rendering Engine Fixes
- Wymuszono użycie systemowego FFMPEG w `J2VMovieRenderer`.
- Naprawiono obsługę akceleracji sprzętowej **NVENC** w kontenerach Docker.
