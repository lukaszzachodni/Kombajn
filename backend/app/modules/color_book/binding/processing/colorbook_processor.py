import os
import glob
from collections import defaultdict
import re
import json
from reportlab.lib.pagesizes import A4

from backend.app.modules.color_book.binding import config
from backend.app.modules.color_book.binding.processing.manuscript_processor import ManuscriptProcessor
from backend.app.modules.color_book.binding.processing.cover_processor import CoverProcessor
from backend.app.modules.color_book.binding.excel_generation.kdp_excel_generator import generate_kdp_excel
from backend.app.modules.color_book.binding.excel_generation.data_transformer import DataTransformer
from backend.app.modules.color_book.binding.helpers.project_data_loader import ProjectDataLoader
from backend.app.modules.color_book.binding.image_utils.line_extraction import extract_black_lines


class ColorbookProcessor:
    def __init__(self, messenger, args):
        self.messenger = messenger
        self.args = args
        self.manuscript_processor = ManuscriptProcessor(messenger, args)
        self.cover_processor = CoverProcessor(messenger, args)
        self.data_transformer = DataTransformer(messenger)
        self.project_data_loader = ProjectDataLoader(messenger)

    def process_all_colorbooks(self):
        base_dir = config.COLORBOOKS_BASE_DIR
        self.messenger.info(f"Starting to process all projects in: {base_dir}")
        for dir_name in os.listdir(base_dir):
            dir_path = os.path.join(base_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue
            self.process_project(dir_path)
        self.messenger.info("All projects processed.")

    def process_project(self, dir_path):
        project_name = os.path.basename(dir_path)
        self.messenger.header(f"Processing: {project_name}")

        images, covers = self._get_project_files(dir_path)
        if not images or not covers:
            return

        project_data = self.project_data_loader.load_and_validate_project_data(
            dir_path, project_name
        )
        if project_data is None:
            return

        images = self._extract_lines_if_needed(images, dir_path)

        sheet_count = len(images)
        common_output_dir = os.path.join(dir_path, "pdf")

        self.manuscript_processor.generate_manuscript(
            output_dir=common_output_dir,
            project_name=project_name,
            images=images,
            sheet_count=sheet_count,
            trim_width=self.args.trim_width,
            trim_height=self.args.trim_height,
        )
        self.cover_processor.generate_covers(
            output_dir=common_output_dir,
            project_data=project_data,
            covers=covers,
            sheet_count=sheet_count,
            trim_width=self.args.trim_width,
            trim_height=self.args.trim_height,
        )

        # Generate KDP Excel file after successful manuscript and cover generation
        excel_data = self.data_transformer.prepare_excel_data(
            project_data, common_output_dir
        )
        if excel_data is None:
            self.messenger.error(
                f"Error preparing Excel data for {project_name}. Aborting Excel generation."
            )
            return

        excel_output_path = os.path.join(
            common_output_dir, f"{project_name}_KDPUploader.xlsx"
        )
        generate_kdp_excel(excel_data, excel_output_path)
        self.messenger.success(
            f"Successfully generated KDP Excel file for {project_name} at {excel_output_path}"
        )

    def _get_project_files(self, dir_path):
        """Finds all page and cover images in a project directory."""
        dir_name = os.path.basename(dir_path)
        images = glob.glob(os.path.join(dir_path, "page*.png"))
        covers = glob.glob(os.path.join(dir_path, "cover*.png"))

        if not images:
            self.messenger.warning(
                f"  Skipping: No page*.png files found in {dir_name}"
            )
        if not covers:
            self.messenger.warning(
                f"  Skipping: No cover*.png files found in {dir_name}"
            )

        return images, covers

    def _extract_lines_if_needed(self, images, dir_path):
        """Extracts black lines from images if the --extract-lines flag is set."""
        if not self.args.extract_lines:
            return images

        self.messenger.info("  Extracting black lines from images...")
        processed_images_dir = os.path.join(dir_path, "processed_images")
        os.makedirs(processed_images_dir, exist_ok=True)
        processed_images = []
        for img_path in images:
            output_path = os.path.join(processed_images_dir, os.path.basename(img_path))
            extract_black_lines(img_path, output_path)
            processed_images.append(output_path)
        self.messenger.success("    Line extraction complete.")
        return processed_images
