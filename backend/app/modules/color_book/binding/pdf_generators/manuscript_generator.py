import os
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class ManuscriptGenerator:
    def __init__(
        self,
        trim_width_in: float,
        trim_height_in: float,
        images: list = [],
        isDoublePagePrint: bool = False,
        output_dir: str = ".",
        sheet_count: int | None = None,
    ):
        self.trim_width_in = trim_width_in
        self.trim_height_in = trim_height_in
        self.images: list = images
        self.output_dir = output_dir
        self.isDoublePagePrint: bool = isDoublePagePrint

        final_sheet_count = sheet_count if sheet_count is not None else len(images) * (0.5 if isDoublePagePrint else 1)

        self._calculate_geometry(final_sheet_count)

        self.interiorCanvas: canvas.Canvas = self._prepareInteriorCanvas()

    def _calculate_geometry(self, sheet_count):
        # Page size with bleed
        bleed = 0.125 * inch
        self.page_width = (self.trim_width_in * inch) + bleed
        self.page_height = (self.trim_height_in * inch) + (2 * bleed)

        # Margins
        self.margin_y = 0.375 * inch
        self.margin_x = 0.375 * inch # Default margin
        if 24 <= sheet_count <= 150:
            self.margin_x = 0.375 * inch
        elif 151 <= sheet_count <= 300:
            self.margin_x = 0.5 * inch
        elif 301 <= sheet_count <= 500:
            self.margin_x = 0.625 * inch
        elif 501 <= sheet_count <= 700:
            self.margin_x = 0.75 * inch
        elif 701 <= sheet_count <= 824:
            self.margin_x = 0.875 * inch

        # Image dimensions
        self.image_width = self.page_width - self.margin_x - self.margin_y
        self.image_height = self.page_height - (2 * self.margin_y)

    def _prepareInteriorCanvas(self):
        pagesize = (self.page_width, self.page_height)
        output_path = os.path.join(self.output_dir, "manuscript.pdf")
        return canvas.Canvas(output_path, pagesize=pagesize)

    def create_pdf(self):
        for image in self.images:
            self.interiorCanvas.drawImage(
                image,
                self.margin_x,
                self.margin_y,
                width=self.image_width,
                height=self.image_height,
            )
            if not self.isDoublePagePrint:
                self.interiorCanvas.showPage()

            self.interiorCanvas.showPage()
        self.interiorCanvas.save()