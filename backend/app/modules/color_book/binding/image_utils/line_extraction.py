import cv2
import numpy as np

def extract_black_lines(image_path, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print(f"Błąd: Nie można wczytać obrazu z {image_path}. Sprawdź ścieżkę pliku.")
        return

    _, binary_image = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

    cv2.imwrite(output_path, binary_image)
    print(f"Obraz z czarnymi liniami został zapisany jako {output_path}")