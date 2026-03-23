#!/bin/bash
# Skrypt do instalacji NVIDIA Container Toolkit wewnątrz WSL2 / Xubuntu

echo "--- Instalacja NVIDIA Container Toolkit ---"

# 1. Dodanie repozytorium NVIDIA
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. Aktualizacja i instalacja
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 3. Konfiguracja Dockera
sudo nvidia-ctk runtime configure --runtime=docker

# 4. Restart Dockera
sudo systemctl restart docker

echo "--- Gotowe! Teraz 'runtime: nvidia' w docker-compose zadziała. ---"
