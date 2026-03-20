# Batch Generation System

To jest plan koncepcyjny systemu "Kombajn AI" służącego do masowego generowania powtarzalnych treści wideo (np. serii Shorts). System opiera się na separacji logiki prezentacji od danych wejściowych.

## Architektura Systemu

System opiera się na trzech filarach:

1. **Szablon Główny (Master Template)**: Plik JSON definiujący strukturę wideo, czasy, pozycje i style. Używa składni zmiennych `{{variable_name}}` w miejscach, które mają być dynamiczne.
2. **Zbiór Danych (Dataset)**: Plik JSON zawierający tablicę obiektów. Klucze w tych obiektach odpowiadają nazwom zmiennych użytych w Szablonie.
3. **Proces Hydratacji (Data Injector)**: Logika systemowa, która iteruje przez Zbiór Danych, podmienia zmienne w Szablonie i generuje gotowe Manifesty dla każdego wideo.

## Struktura Plików

```text
/data
├── /templates
│   └── quiz_master_v1.json        <-- SZABLON (Logika)
│
├── /datasets
│   └── quiz_europe_capitals.json  <-- DANE (Treść dla X filmów)
│
└── /projects
    └── 2026-03-19_batch_id        <-- KAMPANIA (Folder zbiorczy)
        ├── manifest_01.json       <-- Wygenerowany plik dla 1. elementu
        ├── ...
        └── /renders
            ├── quiz_001.mp4
            └── ...
```

## Rozszerzone Możliwości (Roadmap)

* **Dynamiczne Assety**: Użycie słów kluczowych w danych zamiast pełnych ścieżek do plików.
* **Weryfikacja (Pre-flight Check)**: Sprawdzanie długości tekstu przed renderowaniem, aby uniknąć błędów wizualnych.
* **Warianty A/B**: Obsługa różnych stylów kolorystycznych w ramach jednego szablonu przy użyciu logiki warunkowej (`condition`).
