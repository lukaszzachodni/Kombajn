# src/core/genai_project_generator.py
import datetime
import json
import os
from backend.app.modules.color_book.generator.core.genai_integration import GenAIIntegration
from backend.app.modules.color_book.generator.core.project_manager import ProjectManager
from backend.app.modules.color_book.generator.core.prompt_builder import PromptBuilder
from backend.app.modules.color_book.generator.core.statistics_manager import StatisticsManager
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class GenAIProjectGenerator:
    """
    Generates core project data (title, theme, page ideas, etc.) using GenAI.
    Manages interaction with GenAIIntegration, PromptBuilder, and ProjectManager.
    """

    def __init__(
        self,
        genai_integration: GenAIIntegration,
        prompt_builder: PromptBuilder,
        project_manager,
        stats_manager: StatisticsManager,
        settings,
        args,
        console_messenger: ConsoleMessenger,  # Dodaj console_messenger
        imagen_integration,  # Dodaj imagen_integration jeśli jest w __init__
    ):
        self.genai_integration = genai_integration
        self.prompt_builder = prompt_builder
        self.project_manager: ProjectManager = project_manager
        self.stats_manager = stats_manager
        self.settings = settings
        self.args = args
        self.console_messenger = console_messenger
        self.imagen_integration = imagen_integration  # Inicjalizuj imagen_integration

    def generate_project_data(
        self, scheme: dict, page_limit: int
    ) -> tuple[dict | None, str | None]:
        self.console_messenger.info(
            "Generating project data (theme, pages, etc.) using GenAI..."
        )

        user_idea = self.args.idea
        genai_generated_idea = None

        if not user_idea:
            self.console_messenger.info(
                "No specific idea provided. Asking AI to generate a theme...",
                color="CYAN",
            )
            theme_gen_prompt = self.prompt_builder.get_ai_theme_generation_prompt()

            event_theme_gen = self.stats_manager.start_event(
                "AI Theme Generation", "text", prompt=theme_gen_prompt
            )
            genai_generated_idea = self.genai_integration.generate_content_with_config(
                theme_gen_prompt
            )

            if genai_generated_idea:
                self.console_messenger.success(
                    f"AI generated theme: '{genai_generated_idea}'"
                )
            else:
                # ZMIANA: Zamiast przypisywać domyślny pomysł, rzucamy błąd i kończymy zdarzenie jako niepowodzenie.
                self.console_messenger.error(
                    "AI failed to generate a theme. Aborting application."
                )
                self.stats_manager.end_event(
                    event_theme_gen, status="failed", attempts=1
                )
                raise RuntimeError("Failed to generate a theme from AI. Exiting.")
            self.stats_manager.end_event(
                event_theme_gen,
                status="success" if genai_generated_idea else "failed",
                api_response=genai_generated_idea,
            )

        final_idea_prompt = user_idea if user_idea else genai_generated_idea

        prompt_for_project_structure = (
            self.prompt_builder.build_project_generation_prompt(
                idea_prompt=final_idea_prompt,
                scheme=scheme,
                page_limit=page_limit,
            )
        )
        # Usunięto: self.project_manager.save_prompt(self.settings.output_dir, "project_structure_prompt", prompt_for_project_structure)

        event_data_project = self.stats_manager.start_event(
            "Project Data Generation", "text", prompt=prompt_for_project_structure
        )
        json_string_data = self.genai_integration.generate_project(
            prompt_for_project_structure
        )

        if not json_string_data:
            self.console_messenger.error(
                "Failed to generate project data (JSON string)."
            )
            self.stats_manager.end_event(event_data_project, status="failed")

            raise RuntimeError("Failed to generate project data from AI. Exiting.")
        # dodaj tutaj end_event z wygenerowanym projektem
        self.stats_manager.end_event(
            event_data_project, status="success", api_response=json_string_data
        )
        project_files_create = self.stats_manager.start_event(
            "Project files creation", "text"
        )
        # KLUCZOWE: Utwórz folder projektu przed próbą logowania!
        project_title = (
            (
                json_string_data.get("coloringBook", {})
                .get("mainProjectDetails", {})
                .get("title", "untitled_coloring_book")
                .replace(" ", "_")
                .lower()
            )
            if json_string_data
            else "untitled_project"
        )
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )  # ZMIANA: Dodano myślniki w dacie i dwukropki w czasie
        project_folder_name = f"{timestamp}_{project_title}"  # ZMIANA: Zmieniona kolejność na timestamp_tytul
        project_folder = self.project_manager.create_project_folder(project_folder_name)
        if not project_folder:
            self.console_messenger.error(
                "Failed to create project folder. Cannot log API communication or save project data."
            )
            self.stats_manager.end_event(project_files_create, status="failed")
            return None, None
        self.console_messenger.success(f"Project folder created: {project_folder}")

        # Zapisywanie plików konfiguracyjnych do folderu projektu
        self.project_manager.save_config_file(
            project_folder,
            self.settings.project_scheme_path,
            "project_scheme_copy.json",
        )
        self.project_manager.save_config_file(
            project_folder, self.settings.prompts_path, "prompts_copy.json"
        )

        if json_string_data:
            self.console_messenger.debug(
                f"Attempting to save project_data.json. Data: {json_string_data}"
            )
            self.project_manager.save_file(
                project_folder,
                "project_data.json",
                json.dumps(json_string_data, indent=2, ensure_ascii=False),
            )
            saved_file_path = os.path.join(project_folder, "project_data.json")
            if os.path.exists(saved_file_path):
                self.console_messenger.success(
                    f"Project data saved to {saved_file_path}"
                )
            else:
                self.console_messenger.error(
                    f"Project data reported as saved, but file not found at {saved_file_path}"
                )
                self.stats_manager.end_event(
                    project_files_create, status="failed", attempts=1
                )
                raise RuntimeError(
                    "Project data reported as saved, but file not found. Exiting."
                )
        else:
            self.console_messenger.error(
                "No project data to save. Skipping project_data.json creation."
            )
            self.stats_manager.end_event(
                project_files_create, status="failed", attempts=1
            )
            raise RuntimeError("No project data to save. Exiting.")

        self.stats_manager.end_event(project_files_create, status="success")

        return json_string_data, project_folder
