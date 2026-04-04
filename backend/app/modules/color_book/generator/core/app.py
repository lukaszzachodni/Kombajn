import os
from typing import Any, Dict, List, Optional, Tuple

from backend.app.modules.color_book.generator.core.prompt_builder import PromptBuilder
from backend.app.modules.color_book.generator.core.project_manager import ProjectManager
from backend.app.modules.color_book.generator.utils.file_utils import FileUtils
from backend.app.modules.color_book.generator.config.settings import Settings
from backend.app.modules.color_book.generator.core.statistics_manager import StatisticsManager
from backend.app.modules.color_book.generator.core.image_content_generator import ImageContentGenerator
from backend.app.modules.color_book.generator.core.genai_project_generator import GenAIProjectGenerator
from backend.app.modules.color_book.generator.core.app_initializer import AppInitializer
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class App:
    """
    Main application class, orchestrating the entire coloring book generation process.
    """

    def __init__(self) -> None:
        self.settings: Settings = Settings()
        self.console_messenger: ConsoleMessenger = ConsoleMessenger()
        self.project_manager: ProjectManager = ProjectManager(self.settings.output_dir)
        self.prompt_builder: PromptBuilder = PromptBuilder()
        self.stats_manager: StatisticsManager = StatisticsManager(
            self.settings.output_dir, self.settings.stats_filename
        )

        app_initializer: AppInitializer = AppInitializer(
            self.settings, self.stats_manager, self.console_messenger
        )

        (
            self.args,
            self.genai_text_integration,
            self.cover_imagen_integration,
            self.page_imagen_integration,
        ) = app_initializer.initialize_app_components()

        self.image_content_generator: ImageContentGenerator = ImageContentGenerator(
            cover_imagen_integration=self.cover_imagen_integration,
            page_imagen_integration=self.page_imagen_integration,
            prompt_builder=self.prompt_builder,
            project_manager=self.project_manager,
            stats_manager=self.stats_manager,
            settings=self.settings,
            console_messenger=self.console_messenger,
        )

        self.genai_project_generator: GenAIProjectGenerator = GenAIProjectGenerator(
            genai_integration=self.genai_text_integration,
            prompt_builder=self.prompt_builder,
            project_manager=self.project_manager,
            stats_manager=self.stats_manager,
            settings=self.settings,
            args=self.args,
            console_messenger=self.console_messenger,
            imagen_integration=self.cover_imagen_integration,
        )

    def run(self) -> None:
        """
        Main method to run the coloring book generation process.
        """
        if self.args.regenerate:
            self._handle_regeneration()
        else:
            self._run_full_generation()

    def _run_full_generation(self) -> None:
        """
        Runs the full generation process for a new coloring book.
        """
        self.stats_manager.start_run()
        self.console_messenger.info(
            "Starting the generation process...", color="BRIGHT_CYAN"
        )

        scheme_path: str = self.settings.project_scheme_path
        scheme: Optional[Dict] = FileUtils.read_json(scheme_path)
        if not scheme:
            self.console_messenger.error(f"Could not read scheme from {scheme_path}")
            self.stats_manager.end_run()
            self.stats_manager.save_stats()
            return

        genai_project_data: Optional[Dict]
        project_folder: Optional[str]
        genai_project_data, project_folder = (
            self.genai_project_generator.generate_project_data(
                scheme, self.settings.page_limit
            )
        )

        if not genai_project_data or not project_folder:
            self.console_messenger.error(
                "Failed to generate project data or create project folder."
            )
            self.stats_manager.end_run()
            self.stats_manager.save_stats()
            return

        desired_imagen_aspect_ratio: str = "3:4"
        cover_variants: int = (
            self.args.cover_variants
            if self.args.cover_variants is not None
            else self.settings.cover_variants_per_prompt
        )
        page_variants: int = (
            self.args.page_variants
            if self.args.page_variants is not None
            else self.settings.page_variants_per_prompt
        )

        self.image_content_generator.generate_all_cover_types(
            genai_project_data,
            project_folder,
            desired_imagen_aspect_ratio,
            cover_variants,
        )

        self.image_content_generator.generate_pages(
            genai_project_data,
            project_folder,
            desired_imagen_aspect_ratio,
            page_variants,
        )

        self.stats_manager.end_run()
        self.stats_manager.save_stats(project_folder)

        self.console_messenger.success("Generation process completed successfully!")

    def _handle_regeneration(self) -> None:
        """
        Handles the regeneration of a specific item (cover or page).
        """
        self.console_messenger.info("Starting regeneration process...")

        project_path: Optional[str] = self.args.project_path
        item_type: Optional[str] = self.args.item_type
        item_id: Optional[str] = self.args.item_id

        if not all([project_path, item_type, item_id]):
            self.console_messenger.error(
                "For regeneration, you must provide --project-path, --item-type, and --item-id."
            )
            return

        project_data_path: str = os.path.join(project_path, "project_data.json")
        if not os.path.exists(project_data_path):
            self.console_messenger.error(
                f"Project data file not found at {project_data_path}"
            )
            return

        project_data: Optional[Dict] = FileUtils.read_json(project_data_path)
        if not project_data:
            self.console_messenger.error(
                f"Could not read project data from {project_data_path}"
            )
            return

        if item_type == "cover":
            self._regenerate_cover(project_data, project_path, item_id)
        elif item_type == "page":
            self._regenerate_page(project_data, project_path, item_id)
        else:
            self.console_messenger.error(f"Invalid item type: {item_type}")

    def _regenerate_cover(
        self, project_data: Dict, project_path: str, item_id: str
    ) -> None:
        """
        Regenerates a specific cover based on item_id (lang_code, blank_title, or no_text).
        """
        desired_imagen_aspect_ratio: str = "3:4"
        cover_variants: int = (
            self.args.cover_variants
            if self.args.cover_variants is not None
            else self.settings.cover_variants_per_prompt
        )

        if item_id in self.settings.cover_generation_types:
            cover_type: str = item_id
            lang_code: Optional[str] = None
            title: Optional[str] = None
            if cover_type == "full_text":
                self.console_messenger.error(
                    "To regenerate a 'full_text' cover, you must provide a language code (e.g., 'pl') as item-id."
                )
                return
            self.image_content_generator._generate_single_cover_image(
                project_data,
                project_path,
                desired_imagen_aspect_ratio,
                cover_variants,
                cover_type,
                lang_code=lang_code,
                title=title,
            )
        else:
            lang_code = item_id
            cover_type = "full_text"
            language_versions: Dict = project_data.get("coloringBook", {}).get(
                "languageVersions", {}
            )
            lang_data: Optional[Dict] = language_versions.get(lang_code)

            if not lang_data:
                self.console_messenger.error(
                    f"Language version '{lang_code}' not found in project data."
                )
                return
            title = lang_data.get("uploaderData", {}).get("Title", "")
            if not title:
                self.console_messenger.warning(
                    f"No title found for language {lang_code}. Skipping full_text cover regeneration."
                )
                return

            self.image_content_generator._generate_single_cover_image(
                project_data,
                project_path,
                desired_imagen_aspect_ratio,
                cover_variants,
                cover_type,
                lang_code=lang_code,
                title=title,
            )

    def _regenerate_page(
        self, project_data: Dict, project_path: str, page_id: str
    ) -> None:
        """
        Regenerates a specific page.
        """
        self.console_messenger.info(f"Regenerating page: {page_id}")
        pages_data: List[Dict] = (
            project_data.get("coloringBook", {})
            .get("mainProjectDetails", {})
            .get("pageIdeas", [])
        )

        page_to_regenerate: Optional[Dict] = None
        for page in pages_data:
            if str(page.get("pageNumber")) == page_id:
                page_to_regenerate = page
                break

        if not page_to_regenerate:
            self.console_messenger.error(f"Page '{page_id}' not found in project data.")
            return

        desired_imagen_aspect_ratio: str = "3:4"
        page_variants: int = (
            self.args.page_variants
            if self.args.page_variants is not None
            else self.settings.page_variants_per_prompt
        )

        self.image_content_generator.generate_pages(
            project_data,
            project_path,
            desired_imagen_aspect_ratio,
            page_variants,
            pages_to_generate=[page_to_regenerate],
        )
