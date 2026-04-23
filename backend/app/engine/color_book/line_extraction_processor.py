import cv2
import os
from typing import Optional

class LineExtractionProcessor:
    """Procesor odpowiedzialny za optymalizację obrazów AI pod kolorowanki (ekstrakcja linii)."""
    
    def __init__(self, threshold: int = 200):
        self.threshold = threshold

    def process(self, image_path: str, output_path: str) -> bool:
        """Przetwarza obraz i zapisuje wynik jako czarno-biały kontur."""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False

        _, binary_image = cv2.threshold(img, self.threshold, 255, cv2.THRESH_BINARY)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, binary_image)
        return True
