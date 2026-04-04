import json
import datetime
from backend.app.modules.color_book.generator.core.imagen_integration import ImagenIntegration
from backend.app.modules.color_book.generator.core.prompt_builder import PromptBuilder
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class ImageContentGenerator:
    """
    Generates images (cover, pages) using Imagen based on project data.
    """

    def __init__(
        self,
        cover_imagen_integration: ImagenIntegration,
        page_imagen_integration: ImagenIntegration,
        prompt_builder: PromptBuilder,
        project_manager,
        stats_manager,
        settings,
        console_messenger: ConsoleMessenger,
    ):
        self.cover_imagen_integration = cover_imagen_integration
        self.page_imagen_integration = page_imagen_integration
        self.prompt_builder = prompt_builder
        self.project_manager = project_manager
        self.stats_manager = stats_manager
        self.settings = settings
        self.console_messenger = console_messenger
        self.api_log_file_path = None  # Ścieżka do pliku logu API zostanie ustawiona po utworzeniu folderu projektu

    def set_api_log_file_path(self, path: str):
        """Ustawia ścieżkę do pliku logu API dla tej instancji."""
        self.api_log_file_path = path
        self.console_messenger.debug(
            f"Image Content Generator API log path set to: {self.api_log_file_path}"
        )

    def _write_api_log(self, data: dict):
        """Wewnętrzna metoda do zapisu danych do pliku logu API."""
        if not self.api_log_file_path:
            return

        try:
            with open(self.api_log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except IOError as e:
            self.console_messenger.error(
                f"Failed to write to API communication log file {self.api_log_file_path}: {e}"
            )

    def _generate_single_cover_image(
        self,
        project_data: dict,
        project_folder: str,
        aspect_ratio: str,
        num_variants: int,
        cover_type: str,
        lang_code: str = None,
        title: str = None,
    ):
        """
        Generates a cover for a specific language version.
        """
        self.console_messenger.info(f"Generating cover for language: {lang_code}")

        if not title and cover_type == "full_text":
            self.console_messenger.warning(
                f"No title found for language {lang_code}. Skipping full_text cover generation."
            )
            return

        # Create a specific prompt for the language cover
        cover_prompt = self.prompt_builder.get_cover_generation_prompt(
            project_data, cover_type, title
        )

        event_cover_image = self.stats_manager.start_event(
            f"Cover Image Generation ({cover_type}{f' - {lang_code}' if lang_code else ''})",
            "image",
            prompt=cover_prompt,
        )

        cover_images_bytes, attempts = self.cover_imagen_integration.generate_images(
            cover_prompt,
            number_of_images=num_variants,
            aspect_ratio=aspect_ratio,
        )

        if cover_images_bytes:
            for i, image_bytes in enumerate(cover_images_bytes):
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                image_name_suffix = f"_{lang_code}" if lang_code else ""
                image_name = (
                    f"cover_{cover_type}{image_name_suffix}_{timestamp}_v{i+1}"
                    if num_variants > 1
                    else f"cover_{cover_type}{image_name_suffix}_{timestamp}"
                )
                self.project_manager.save_image(project_folder, image_name, image_bytes)

            self.stats_manager.end_event(
                event_cover_image, status="success", attempts=attempts
            )
            self.console_messenger.success(
                f"{len(cover_images_bytes)} {cover_type} cover image variant(s) for {lang_code if lang_code else 'universal'} generated and saved in {project_folder}."
            )
        else:
            self.stats_manager.end_event(
                event_cover_image, status="failed", attempts=attempts
            )
            self.console_messenger.error(
                f"Failed to generate {cover_type} cover image for {lang_code if lang_code else 'universal'}."
            )

    def generate_all_cover_types(
        self,
        project_data: dict,
        project_folder: str,
        aspect_ratio: str,
        num_variants: int,
    ):
        """
        Generates all specified types of covers (full_text for each language, blank_title, no_text).
        """
        cover_types_to_generate = self.settings.cover_generation_types

        for cover_type in cover_types_to_generate:
            if cover_type == "full_text":
                language_versions = project_data.get("coloringBook", {}).get(
                    "languageVersions", {}
                )
                for lang_code, lang_data in language_versions.items():
                    title = (
                        lang_data.get("uploaderData", {})
                        .get("Title", "")
                        .replace(":", "")
                    )
                    while "  " in title:
                        title = title.replace("  ", " ")

                    self._generate_single_cover_image(
                        project_data,
                        project_folder,
                        aspect_ratio,
                        num_variants,
                        cover_type,
                        lang_code=lang_code,
                        title=title,
                    )
            elif cover_type == "blank_title":
                self._generate_single_cover_image(
                    project_data,
                    project_folder,
                    aspect_ratio,
                    num_variants,
                    cover_type,
                )
            elif cover_type == "no_text":
                self._generate_single_cover_image(
                    project_data,
                    project_folder,
                    aspect_ratio,
                    num_variants,
                    cover_type,
                )
            else:
                self.console_messenger.warning(
                    f"Unknown cover type specified: {cover_type}. Skipping."
                )

    def generate_pages(
        self,
        project_data: dict,
        project_folder: str,
        aspect_ratio: str,
        num_variants: int,
        pages_to_generate: list = None,
    ):
        """
        Generates and saves images for each page of the coloring book.
        """
        self.console_messenger.info("Generating coloring pages...")
        if (
            not self.page_imagen_integration
            or not self.page_imagen_integration.image_model
        ):
            self.console_messenger.warning(
                "Imagen model for pages not initialized. Skipping page generation."
            )
            return

        pages_data = (
            pages_to_generate
            if pages_to_generate
            else project_data.get("coloringBook", {})
            .get("mainProjectDetails", {})
            .get("pageIdeas", [])
        )
        if not pages_data:
            self.console_messenger.warning(
                "No pages defined in project data. Skipping page generation."
            )
            return

        for i, page_idea_entry in enumerate(pages_data):
            if (
                self.settings.page_limit is not None
                and i >= self.settings.page_limit
                and not pages_to_generate  # Apply test limit only when not regenerating
            ):
                self.console_messenger.info(
                    f"Limit of {self.settings.page_limit} pages reached. Skipping remaining pages.",
                    color="YELLOW",
                )
                break
            page_number = page_idea_entry.get("pageNumber", i + 1)
            self.console_messenger.info(f"Generating page {page_number}...")

            page_prompt = self.prompt_builder.get_page_generation_prompt(
                page_idea_entry, project_data
            )
            # Usunięto: self.project_manager.save_prompt(project_folder, f"page_{page_number}_image_prompt", page_prompt)

            event_page_image = self.stats_manager.start_event(
                f"Page {page_number} Image Generation",
                "image",
                prompt=page_prompt,
                page_number=page_number,
            )
            page_images_bytes, attempts = self.page_imagen_integration.generate_images(
                page_prompt,
                number_of_images=num_variants,
                aspect_ratio=aspect_ratio,
            )

            if page_images_bytes:
                for i, image_bytes in enumerate(page_images_bytes):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    image_name = (
                        f"page_{page_number:03d}_{timestamp}_v{i+1}"
                        if len(page_images_bytes) > 1
                        else f"page_{page_number:03d}_{timestamp}"
                    )
                    self.project_manager.save_image(
                        project_folder, image_name, image_bytes
                    )

                self.stats_manager.end_event(
                    event_page_image, status="success", attempts=attempts
                )
                self.console_messenger.success(
                    f"{len(page_images_bytes)} image variant(s) for Page {page_number} generated and saved in {project_folder}."
                )
            else:
                self.stats_manager.end_event(
                    event_page_image, status="failed", attempts=attempts
                )

                self.console_messenger.error(
                    f"Failed to generate image for Page {page_number}."
                )
