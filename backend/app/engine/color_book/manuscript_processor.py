import os
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from typing import List

class ManuscriptProcessor:
    """Procesor odpowiedzialny za składanie manuskryptu kolorowanki w formacie PDF."""
    
    def __init__(
        self,
        trim_width_in: float = 8.5,
        trim_height_in: float = 11.0,
        output_dir: str = "."
    ):
        self.trim_width_in = trim_width_in
        self.trim_height_in = trim_height_in
        self.output_dir = output_dir

    def generate(self, images: List[str], output_filename: str = "manuscript.pdf") -> str:
        """Generuje PDF z dostarczonych ścieżek do obrazów."""
        output_path = os.path.join(self.output_dir, output_filename)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Obliczenia geometrii (z uproszczonym bleedem)
        bleed = 0.125 * inch
        page_width = (self.trim_width_in * inch) + bleed
        page_height = (self.trim_height_in * inch) + (2 * bleed)
        
        # Marginesy (uproszczone dla orkiestratora)
        margin_x = 0.375 * inch
        margin_y = 0.375 * inch
        
        image_width = page_width - margin_x - (0.375 * inch)
        image_height = page_height - (2 * margin_y)

        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        for img_path in images:
            if os.path.exists(img_path):
                c.drawImage(
                    img_path,
                    margin_x,
                    margin_y,
                    width=image_width,
                    height=image_height,
                )
                # Pusta strona po każdym obrazku (standard w kolorowankach KDP)
                c.showPage()
                c.showPage()
                
        c.save()
        return output_path
