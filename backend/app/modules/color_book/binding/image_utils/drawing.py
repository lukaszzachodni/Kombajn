import os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from backend.app.modules.color_book.binding import config


class CoverDrawer:
    def __init__(
        self,
        canvas: canvas.Canvas,
        cover_image: str,
        images: list,
        cover_dimensions: dict,
        title: str,
        draw_title: bool,
    ):
        self.canvas = canvas
        self.cover_image = cover_image
        self.images = images
        self.cover_dimensions = cover_dimensions
        self.title = title
        self.draw_title = draw_title
        self.default_font = "Helvetica"
        self.bold_font = "Helvetica-Bold"
        self._register_fonts()

    def _register_fonts(self):
        try:
            pdfmetrics.registerFont(
                TTFont("ComicNeue-Regular", config.DEFAULT_FONT_PATH)
            )
            pdfmetrics.registerFont(TTFont("ComicNeue-Bold", config.BOLD_FONT_PATH))
            self.default_font = "ComicNeue-Regular"
            self.bold_font = "ComicNeue-Bold"
        except Exception as e:
            print(f"Warning: Could not load custom font. Using 'Helvetica'. Error: {e}")

    def draw_cover(self):
        self.canvas.setFillColorRGB(random.random(), random.random(), random.random())
        self.canvas.rect(
            0,
            0,
            self.cover_dimensions["full_cover"]["width"] * mm,
            self.cover_dimensions["full_cover"]["height"] * mm,
            fill=1,
            stroke=0,
        )
        self._drawFrontCover()
        self._drawBackCover()
        self.canvas.save()

    def _drawBackCover(self):
        tinyFactor = 0.4
        tinyWidth = (
            self.cover_dimensions["front_cover"]["width"] * mm * tinyFactor
        )
        tinyHeight = (
            self.cover_dimensions["front_cover"]["height"] * mm * tinyFactor
        )
        yMargin = (
            self.cover_dimensions["front_cover"]["height"] * mm
            - (2 * tinyHeight)
        ) / 4
        xMargin = (
            self.cover_dimensions["front_cover"]["width"] * mm
            - (2 * tinyWidth)
        ) / 4
        xLeftRow = self.cover_dimensions["bleed"]["width"] * mm + xMargin
        xRightRow = (
            self.cover_dimensions["bleed"]["width"] * mm
            + xMargin
            + tinyWidth
            + xMargin
            + xMargin
        )
        yTopRow = (
            self.cover_dimensions["bleed"]["height"] * mm
            + yMargin
            + tinyHeight
            + yMargin
            + yMargin
        )
        yBottomRow = self.cover_dimensions["bleed"]["height"] * mm + yMargin

        def draw_and_remove_image(x, y, width, height):
            if not self.images:
                print("Warning: No more images available to draw.")
                return
            image_index = random.randrange(0, len(self.images))
            self.canvas.drawImage(
                self.images[image_index],
                x=x,
                y=y,
                width=width,
                height=height,
            )
            self.canvas.rect(
                x=x,
                y=y,
                width=width,
                height=height,
                fill=0,
                stroke=1,
            )
            self.images.pop(image_index)

        draw_and_remove_image(xLeftRow, yTopRow, tinyWidth, tinyHeight)
        draw_and_remove_image(xRightRow, yTopRow, tinyWidth, tinyHeight)
        draw_and_remove_image(xLeftRow, yBottomRow, tinyWidth, tinyHeight)
        draw_and_remove_image(xRightRow, yBottomRow, tinyWidth, tinyHeight)

        xMiddle = (
            self.cover_dimensions["bleed"]["width"] * mm
            + (self.cover_dimensions["front_cover"]["width"] * mm / 2)
            - (tinyWidth / 2)
        )
        yMiddle = (
            self.cover_dimensions["bleed"]["height"] * mm
            + (self.cover_dimensions["front_cover"]["height"] * mm / 2)
            - (tinyHeight / 2)
        )

        draw_and_remove_image(xMiddle, yMiddle, tinyWidth, tinyHeight)

        self.canvas.showPage()

    def _drawFrontCover(self):
        x = (
            self.cover_dimensions["full_cover"]["width"] * mm
            - self.cover_dimensions["front_cover"]["width"] * mm
            - self.cover_dimensions["spine"]["width"] * mm / 2
        )
        y = 0

        self.canvas.drawImage(
            self.cover_image,
            x=x,
            y=y,
            width=self.cover_dimensions["front_cover"]["width"] * mm
            + self.cover_dimensions["bleed"]["width"] * mm,
            height=self.cover_dimensions["front_cover"]["height"] * mm
            + 2 * self.cover_dimensions["bleed"]["height"] * mm,
        )

        if self.draw_title:
            self._drawTitle(x, y)

    def _draw_placeholder(self, x, y, width, height, radius, color, alpha):
        self.canvas.setFillColorRGB(color[0], color[1], color[2], alpha)
        self.canvas.roundRect(x, y, width, height, radius, fill=1, stroke=0)

    def _draw_text(self, text, x, y, font_name, font_size, color, align="center"):
        self.canvas.setFont(font_name, font_size)
        self.canvas.setFillColorRGB(color[0], color[1], color[2])
        if align == "center":
            self.canvas.drawCentredString(text=text, x=x, y=y)
        elif align == "left":
            self.canvas.drawString(text=text, x=x, y=y)
        elif align == "right":
            self.canvas.drawRightString(text=text, x=x, y=y)

    def _wrap_text(self, text, font_name, font_size, max_width):
        lines = []
        words = text.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if self.canvas.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def _drawTitle(self, front_cover_x, front_cover_y):
        initial_main_font_size = 48
        min_font_size = 24
        MAINTITLE_LINE_SPACING_FACTOR = 0.5
        SUBTITLE_LINE_SPACING_FACTOR = 1.5
        RECT_TOP_PADDING_MM = 15 * mm
        RECT_BOTTOM_PADDING_MM = 5 * mm
        SUBTITLE_SPACING_MM = 2 * mm  # Reduced from 5 * mm

        # 20mm padding on each side of the front cover
        max_text_width = (
            self.cover_dimensions["front_cover"]["width"] * mm
        ) - (40 * mm)

        main_title_text = self.title
        subtitle_text = ""

        if ":" in self.title:
            parts = self.title.split(":", 1)
            main_title_text = parts[0].strip()
            subtitle_text = parts[1].strip()

        # --- Process Main Title ---
        current_main_font_size = initial_main_font_size
        while (
            self.canvas.stringWidth(
                main_title_text, self.bold_font, current_main_font_size
            )
            > max_text_width
            and current_main_font_size > min_font_size
        ):
            current_main_font_size -= 2
        main_title_lines = self._wrap_text(
            main_title_text, self.bold_font, current_main_font_size, max_text_width
        )
        main_line_height = current_main_font_size * MAINTITLE_LINE_SPACING_FACTOR
        total_main_height = len(main_title_lines) * main_line_height

        # --- Process Subtitle (if exists) ---
        current_subtitle_font_size = 0
        subtitle_lines = []
        total_subtitle_height = 0
        actual_subtitle_spacing = 0

        if subtitle_text:
            current_subtitle_font_size = int(
                current_main_font_size * 0.6
            )  # Subtitle will be 60% of main title font size
            if current_subtitle_font_size < min_font_size:
                current_subtitle_font_size = min_font_size

            while (
                self.canvas.stringWidth(
                    subtitle_text, self.default_font, current_subtitle_font_size
                )
                > max_text_width
                and current_subtitle_font_size > min_font_size
            ):
                current_subtitle_font_size -= 2
            subtitle_lines = self._wrap_text(
                subtitle_text,
                self.default_font,
                current_subtitle_font_size,
                max_text_width,
            )
            subtitle_line_height = (
                current_subtitle_font_size * SUBTITLE_LINE_SPACING_FACTOR
            )
            total_subtitle_height = len(subtitle_lines) * subtitle_line_height
            actual_subtitle_spacing = SUBTITLE_SPACING_MM

        total_text_block_height = (
            total_main_height + actual_subtitle_spacing + total_subtitle_height
        )

        # Calculate x_center relative to the front cover
        front_cover_width = (
            self.cover_dimensions["front_cover"]["width"] * mm
        )
        x_center_front_cover = front_cover_x + (front_cover_width / 2)

        # Target vertical center for the text block
        target_y_center = (
            front_cover_y
            + self.cover_dimensions["front_cover"]["height"] * mm
            - 50 * mm
        )

        # Calculate placeholder dimensions and position
        max_overall_line_width = 0
        for line in main_title_lines:
            max_overall_line_width = max(
                max_overall_line_width,
                self.canvas.stringWidth(line, self.bold_font, current_main_font_size),
            )
        for line in subtitle_lines:
            max_overall_line_width = max(
                max_overall_line_width,
                self.canvas.stringWidth(
                    line, self.default_font, current_subtitle_font_size
                ),
            )

        rect_width = max_overall_line_width + (
            2 * RECT_TOP_PADDING_MM
        )  # Use top padding for horizontal padding too
        rect_height = (
            total_text_block_height + RECT_TOP_PADDING_MM + RECT_BOTTOM_PADDING_MM
        )

        rect_x = x_center_front_cover - rect_width / 2
        rect_y = (
            target_y_center - (total_text_block_height / 2) - RECT_BOTTOM_PADDING_MM
        )

        self._draw_placeholder(
            rect_x, rect_y, rect_width, rect_height, 10 * mm, (0.9, 0.9, 0.9), 0.8
        )

        # Draw each line of text
        # Calculate the baseline for the first line of the main title
        current_y_baseline = (
            target_y_center + (total_text_block_height / 2) - (main_line_height / 2)
        )

        # Draw main title lines
        for i, line in enumerate(main_title_lines):
            line_y = current_y_baseline - (i * main_line_height)
            self._draw_text(
                line,
                x_center_front_cover,
                line_y,
                self.bold_font,
                current_main_font_size,
                (0.1, 0.1, 0.1),
            )

        # Adjust current_y_baseline for subtitle if present
        if subtitle_text:
            current_y_baseline -= total_main_height + actual_subtitle_spacing
            # Calculate baseline for the first line of the subtitle
            subtitle_first_line_baseline_y = current_y_baseline - (
                subtitle_line_height / 2
            )

            # Draw subtitle lines
            for i, line in enumerate(subtitle_lines):
                line_y = subtitle_first_line_baseline_y - (i * subtitle_line_height)
                self._draw_text(
                    line,
                    x_center_front_cover,
                    line_y,
                    self.default_font,
                    current_subtitle_font_size,
                    (0.1, 0.1, 0.1),
                )