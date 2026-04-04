class CoverCalculator:
    """
    Calculates KDP cover dimensions based on book specifications.
    """

    INCH_TO_MM = 25.4
    BLEED_MM = 3.17
    SPINE_MARGIN_MM = 1.59
    BARCODE_MARGIN_MM = 6.35

    SPINE_MULTIPLIER = {
        'paperback': {
            'white': 0.002252,  # inches per page
            'cream': 0.0025,    # inches per page
        },
        'hardcover': {
            # TODO: Add hardcover values if needed
        }
    }

    def __init__(self, trim_width_in, trim_height_in, page_count, paper_type='white', binding_type='paperback'):
        self.trim_width_in = trim_width_in
        self.trim_height_in = trim_height_in
        self.page_count = page_count
        self.paper_type = paper_type
        self.binding_type = binding_type

        self._calculate()

    def _calculate(self):
        # Calculations in mm
        self.trim_width_mm = self.trim_width_in * self.INCH_TO_MM
        self.trim_height_mm = self.trim_height_in * self.INCH_TO_MM

        self.spine_width_mm = self._calculate_spine_width()

        self.full_cover_width_mm = (self.trim_width_mm * 2) + self.spine_width_mm + (self.BLEED_MM * 2)
        self.full_cover_height_mm = self.trim_height_mm + (self.BLEED_MM * 2)

        self.front_cover_width_mm = self.trim_width_mm
        self.front_cover_height_mm = self.trim_height_mm

        self.safe_area_width_mm = self.trim_width_mm - self.BLEED_MM
        self.safe_area_height_mm = self.trim_height_mm - self.BLEED_MM

        self.spine_safe_area_width_mm = self.spine_width_mm - (self.SPINE_MARGIN_MM * 2)
        self.spine_safe_area_height_mm = self.trim_height_mm - (self.BLEED_MM * 2)


    def _calculate_spine_width(self):
        multiplier = self.SPINE_MULTIPLIER.get(self.binding_type, {}).get(self.paper_type)
        if not multiplier:
            raise ValueError(f"Unsupported binding/paper type: {self.binding_type}/{self.paper_type}")

        spine_in = self.page_count * multiplier
        return spine_in * self.INCH_TO_MM

    def get_dimensions_dict(self):
        """Returns a dictionary with all calculated dimensions in mm."""
        return {
            "full_cover": {
                "width": round(self.full_cover_width_mm, 2),
                "height": round(self.full_cover_height_mm, 2)
            },
            "front_cover": {
                "width": round(self.front_cover_width_mm, 2),
                "height": round(self.front_cover_height_mm, 2)
            },
            "safe_area": {
                "width": round(self.safe_area_width_mm, 2),
                "height": round(self.safe_area_height_mm, 2)
            },
            "bleed": {
                "width": self.BLEED_MM,
                "height": self.BLEED_MM
            },
            "margin": {
                "width": self.BLEED_MM,
                "height": self.BLEED_MM
            },
            "spine": {
                "width": round(self.spine_width_mm, 2),
                "height": round(self.front_cover_height_mm, 2)
            },
            "spine_safe_area": {
                "width": round(self.spine_safe_area_width_mm, 2) if self.spine_safe_area_width_mm > 0 else 0,
                "height": round(self.spine_safe_area_height_mm, 2)
            },
            "spine_margin": {
                "width": self.SPINE_MARGIN_MM,
                "height": self.SPINE_MARGIN_MM
            },
            "barcode_margin": {
                "width": self.BARCODE_MARGIN_MM,
                "height": self.BARCODE_MARGIN_MM
            }
        }
