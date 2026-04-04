import os
from reportlab.lib.pagesizes import A4
from backend.app.modules.color_book.binding.pdf_generators.manuscript_generator import ManuscriptGenerator
from backend.app.modules.color_book.binding import config

class ManuscriptProcessor:
    def __init__(self, messenger, args):
        self.messenger = messenger
        self.args = args

    def generate_manuscript(self, output_dir, project_name, images, sheet_count, trim_width, trim_height):
        """Generates the manuscript PDF for a project."""
        manuscript_pdf_path = os.path.join(output_dir, "manuscript.pdf")

        if os.path.exists(manuscript_pdf_path) and not self.args.re_do:
            self.messenger.info(
                f"  Manuscript already exists in {output_dir} (use --re-do to force reprocessing)"
            )
            return

        self.messenger.info(f"  Generating manuscript for {project_name}")
        try:
            os.makedirs(output_dir, exist_ok=True)
            manuscript_gen = ManuscriptGenerator(
                trim_width_in=trim_width,
                trim_height_in=trim_height,
                images=images.copy(),
                isDoublePagePrint=False,
                output_dir=output_dir,
                sheet_count=sheet_count,
            )
            manuscript_gen.create_pdf()
            self.messenger.success(
                f'    Successfully created manuscript in "{output_dir}"'
            )
        except Exception as e:
            self.messenger.error(
                f"    Error creating manuscript for {project_name}: {e}"
            )
            if os.path.exists(output_dir) and not os.listdir(output_dir):
                try:
                    os.rmdir(output_dir)
                    self.messenger.info(
                        f"    Removed empty manuscript directory after error: {output_dir}"
                    )
                except OSError as e_rm:
                    self.messenger.warning(
                        f"    Could not remove empty manuscript directory {output_dir}: {e_rm}"
                    )