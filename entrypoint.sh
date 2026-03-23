#!/bin/bash
# Sprawdź czy sterownik NVIDIA jest widoczny w kontenerze
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "--- [Kombajn] Wykryto GPU NVIDIA. Używam akceleracji sprzętowej. ---"
else
    echo "--- [Kombajn] Brak dostępu do GPU NVIDIA. Działam w trybie CPU. ---"
fi

# Uruchom główny proces aplikacji
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
