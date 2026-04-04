import os
import glob
from collections import defaultdict
import re
import json
from reportlab.lib.pagesizes import A4
from backend.app.modules.color_book.binding.pdf_generators.cover_generator import CoverGenerator
from backend.app.modules.color_book.binding.pdf_generators.cover_calculator import CoverCalculator
from backend.app.modules.color_book.binding import config

class CoverProcessor:
    def __init__(self, messenger, args):
        self.messenger = messenger
        self.args = args

    def generate_covers(self, output_dir, project_data, covers, sheet_count, trim_width, trim_height):
        """Generates covers for each language version specified in project_data."""
        # Find the base cover image (cover_no_text*.png)
        no_text_covers = [
            c
            for c in covers
            if os.path.basename(c).startswith("cover_no_text") and c.endswith(".png")
        ]

        if not no_text_covers:
            self.messenger.error(
                "  Error: No cover_no_text*.png found in project. Skipping cover generation."
            )
            return

        # Get the latest cover_no_text image
        base_cover_path = max(no_text_covers, key=os.path.getctime)
        self.messenger.info(
            f"  Using base cover image: {os.path.basename(base_cover_path)}"
        )

        # Calculate dimensions once
        calculator = CoverCalculator(
            trim_width_in=trim_width,
            trim_height_in=trim_height,
            page_count=sheet_count * 2 # sheet_count is the number of pages with images, but page_count for spine is total pages
        )
        cover_dims = calculator.get_dimensions_dict()

        # Save calculated dimensions to a file
        trim_calc_path = os.path.join(output_dir, "trim_calc.json")
        if not os.path.exists(trim_calc_path) or self.args.re_do:
            os.makedirs(output_dir, exist_ok=True)
            with open(trim_calc_path, 'w') as f:
                json.dump(cover_dims, f, indent=4)
            self.messenger.info(f'  Saved trim calculations to {trim_calc_path}')

        for lang_code, lang_data in project_data["coloringBook"][
            "languageVersions"
        ].items():
            title = lang_data.get("uploaderData", {}).get("Title", "")

            if not title:
                self.messenger.warning(
                    f"  Warning: No title found for language {lang_code}. Skipping cover for this language."
                )
                continue

            # Use the base cover image for all language versions
            self._generate_single_cover(
                output_dir=output_dir,
                project_name=project_data["coloringBook"]["mainProjectDetails"][
                    "title"
                ],
                cover_path=base_cover_path,
                lang_code=lang_code,
                title_to_draw=title,
                cover_dimensions=cover_dims
            )

    def _group_covers_by_type(self, covers):
        """Groups cover image paths by their base name (e.g., 'cover_pl')."""
        grouped_covers_by_type = defaultdict(list)
        timestamp_regex = re.compile(r"_\d{14}$")

        for cover_path in covers:
            filename_without_ext = os.path.splitext(os.path.basename(cover_path))[0]
            cover_type = timestamp_regex.sub("", filename_without_ext)
            grouped_covers_by_type[cover_type].append(cover_path)

        return grouped_covers_by_type

    def _generate_single_cover(
        self,
        output_dir,
        project_name,
        cover_path,
        lang_code,
        title_to_draw,
        cover_dimensions
    ):
        """Generates a single cover PDF with a language-specific title and filename."""
        original_cover_filename = os.path.basename(cover_path)
        cover_pdf_filename = (
            f"{lang_code}_{os.path.splitext(original_cover_filename)[0]}.pdf"
        )
        cover_pdf_path = os.path.join(output_dir, cover_pdf_filename)

        if os.path.exists(cover_pdf_path) and not self.args.re_do:
            self.messenger.info(
                f"  Skipping: Cover PDF {cover_pdf_filename} already exists (use --re-do)"
            )
            return

        self.messenger.info(
            f"  Processing cover for {lang_code}: {original_cover_filename}"
        )
        try:
            os.makedirs(output_dir, exist_ok=True)

            cover_gen = CoverGenerator(
                cover_image=cover_path,
                title=title_to_draw,
                output_dir=output_dir,
                draw_title=self.args.draw_title,
                cover_dimensions=cover_dimensions
            )
            # Override the output filename for CoverGenerator
            cover_gen.coverCanvas._filename = cover_pdf_path
            cover_gen.create_pdf()
            self.messenger.success(
                f'    Successfully created cover PDF {cover_pdf_filename} in "{output_dir}"'
            )
        except Exception as e:
            self.messenger.error(
                f"    Error creating cover PDF {cover_pdf_filename} for {project_name}: {e}"
            )
