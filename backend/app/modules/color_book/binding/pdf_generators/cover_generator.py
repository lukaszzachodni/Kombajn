import os
from reportlab.lib.pagesizes import *
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
import random
from backend.app.modules.color_book.binding.image_utils.drawing import CoverDrawer

class CoverGenerator:
    def __init__(
        self,
        cover_image: str | None = None,
        title="book",
        output_dir: str = ".",
        draw_title: bool = False,
        cover_dimensions: dict = None,
    ):
        self.title = title
        self.cover_image = cover_image
        self.output_dir = output_dir
        self.draw_title = draw_title
        self.cover_dimensions = cover_dimensions

        self.coverCanvas: canvas.Canvas = self._prepareCoverCanvas()

        self.cover_drawer = CoverDrawer(
            canvas=self.coverCanvas,
            cover_image=self.cover_image,
            images=[], # No images needed for cover drawing logic
            cover_dimensions=self.cover_dimensions,
            title=self.title,
            draw_title=self.draw_title
        )

    def _prepareCoverCanvas(self):
        coverSize = (
            self.cover_dimensions["full_cover"]["width"] * mm,
            self.cover_dimensions["full_cover"]["height"] * mm,
        )
        # Use the original cover image filename to name the PDF
        original_filename = os.path.basename(self.cover_image)
        pdf_filename = os.path.splitext(original_filename)[0] + ".pdf"
        output_path = os.path.join(self.output_dir, pdf_filename)
        return canvas.Canvas(output_path, pagesize=coverSize)

    def create_pdf(self):
        self.cover_drawer.draw_cover()