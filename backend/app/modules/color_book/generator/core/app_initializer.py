import argparse
import sys
from typing import List, Tuple, Optional

from backend.app.modules.color_book.generator.config.settings import Settings
from backend.app.modules.color_book.generator.core.genai_integration import GenAIIntegration
from backend.app.modules.color_book.generator.core.imagen_integration import ImagenIntegration
from backend.app.modules.color_book.generator.core.statistics_manager import StatisticsManager
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class AppInitializer:
    """
    Responsible for initializing key application components:
    CLI argument parsing, AI model selection, and integration setup.
    """

    def __init__(
        self,
        settings: Settings,
        stats_manager: StatisticsManager,
        console_messenger: ConsoleMessenger,
    ) -> None:
        self.settings: Settings = settings
        self.stats_manager: StatisticsManager = stats_manager
        self.console_messenger: ConsoleMessenger = console_messenger

    def _parse_arguments(self) -> argparse.Namespace:
        """
        Parses command-line arguments for model selection and user idea.
        """
        parser = argparse.ArgumentParser(
            description="Generate coloring books using AI models.", add_help=False
        )
        parser.add_argument(
            "--genai-model",
            type=str,
            default=self.settings.genai_model_default,
            help="Specify the GenAI model to use (e.g., gemini-1.5-flash-latest). Use '?' for interactive selection.",
        )
        parser.add_argument(
            "--cover-imagen-model",
            type=str,
            default=self.settings.imagen_cover_model_default,
            help="Specify the Imagen model for the cover (e.g., imagegeneration@006). Use '?' for interactive selection.",
        )
        parser.add_argument(
            "--page-imagen-model",
            type=str,
            default=self.settings.imagen_page_model_default,
            help="Specify the Imagen model for the pages (e.g., imagegeneration@005). Use '?' for interactive selection.",
        )
        parser.add_argument(
            "--idea",
            type=str,
            help="Provide a custom idea for the coloring book theme (e.g., 'dinosaurs in space'). If not provided, AI will generate one.",
        )

        parser.add_argument(
            "--cover_variants",
            type=int,
            help="Number of image variants to generate for each prompt. Overrides the default from .env.",
            default=None,
        )
        parser.add_argument(
            "--page_variants",
            type=int,
            help="Number of image variants to generate for each prompt. Overrides the default from .env.",
            default=None,
        )
        parser.add_argument(
            "--cover-types",
            type=lambda s: [item.strip() for item in s.split(",")],
            default=None,
            help="Comma-separated list of cover types to generate (e.g., 'full_text,blank_title,no_text'). Overrides the default from .env.",
        )
        parser.add_argument(
            "-h", "--help", action="store_true", help="Show this help message and exit."
        )

        parser.add_argument(
            "--regenerate", action="store_true", help="Enable regeneration mode."
        )
        parser.add_argument(
            "--project-path",
            type=str,
            help="Path to the project folder for regeneration.",
        )
        parser.add_argument(
            "--item-type",
            type=str,
            choices=["cover", "page"],
            help="Type of item to regenerate (cover or page).",
        )
        parser.add_argument(
            "--item-id",
            type=str,
            help="ID of the item to regenerate (e.g., 'pl' for cover, '17' for page).",
        )

        args, unknown_args = parser.parse_known_args()

        if args.help:
            parser.print_help()
            self.console_messenger.info(
                "\nAvailable GenAI models from .env: "
                + ", ".join(self.settings.genai_model_names)
            )
            if self.settings.imagen_model_names:
                self.console_messenger.info(
                    "Available Imagen models from .env: "
                    + ", ".join(self.settings.imagen_model_names)
                )
            else:
                self.console_messenger.info("No Imagen models configured in .env.")
            sys.exit(0)

        return args

    def _select_model_interaktywnie(
        self, model_type: str, available_models: List[str], default_index: int
    ) -> Optional[str]:
        """
        Guides interactive model selection from a given list.
        Returns the selected model name or None if the list is empty.
        """
        if not available_models:
            self.console_messenger.info(
                f"No {model_type} models available to choose from."
            )
            self.console_messenger.warning(
                f"No {model_type} models available to choose from."
            )
            return None

        default_model: Optional[str] = (
            available_models[default_index]
            if available_models and 0 <= default_index < len(available_models)
            else None
        )

        while True:
            self.console_messenger.section_header(f"{model_type} Model Selection")
            for i, model in enumerate(available_models):
                self.console_messenger.info(f"  {i+1}. {model}")

            prompt_suffix: str = f" (Default: {default_model})" if default_model else ""
            user_input: str = input(
                self.console_messenger._colorize_message(
                    f"Enter the number corresponding to your choice{prompt_suffix}: ",
                    "BRIGHT_BLUE",
                )
            ).strip()

            if not user_input:
                if default_model:
                    self.console_messenger.info(
                        f"Using default {model_type} model: '{default_model}'.",
                        color="GREEN",
                    )
                    return default_model
                else:
                    self.console_messenger.warning(
                        "No default model available and no selection made. Please choose one or configure models in .env."
                    )
                    continue

            try:
                choice_index: int = int(user_input) - 1
                if 0 <= choice_index < len(available_models):
                    selected_model: str = available_models[choice_index]
                    self.console_messenger.info(
                        f"You selected {model_type} model: '{selected_model}'.",
                        color="GREEN",
                    )
                    return selected_model
                else:
                    self.console_messenger.warning(
                        "Invalid number. Please choose a number from the list."
                    )
            except ValueError:
                self.console_messenger.warning("Invalid input. Please enter a number.")

    def initialize_app_components(
        self,
    ) -> Tuple[
        argparse.Namespace,
        GenAIIntegration,
        Optional[ImagenIntegration],
        Optional[ImagenIntegration],
    ]:
        """
        Initializes and returns parsed CLI arguments,
        and configured GenAIIntegration and ImagenIntegration instances.
        """
        args: argparse.Namespace = self._parse_arguments()

        genai_current_model: Optional[str] = None
        selected_genai_model_from_args: Optional[str] = args.genai_model

        if (
            selected_genai_model_from_args
            and selected_genai_model_from_args != "?"
            and selected_genai_model_from_args in self.settings.genai_model_names
        ):
            genai_current_model = selected_genai_model_from_args
            self.console_messenger.info(
                f"GenAI model selected from arguments: '{genai_current_model}'.",
                color="BRIGHT_BLUE",
            )
        else:
            self.console_messenger.section_header("GenAI Model Selection")
            genai_current_model = self._select_model_interaktywnie(
                model_type="GenAI (text generation)",
                available_models=self.settings.genai_model_names,
                default_index=0,
            )
            if not genai_current_model:
                self.console_messenger.error("GenAI model not selected. Exiting.")
                sys.exit(1)

        cover_current_model: Optional[str] = None
        cover_model_from_args: Optional[str] = args.cover_imagen_model

        if (
            cover_model_from_args
            and cover_model_from_args != "?"
            and cover_model_from_args in self.settings.imagen_model_names
        ):
            cover_current_model = cover_model_from_args
            self.console_messenger.info(
                f"Cover Imagen model selected from arguments: '{cover_current_model}'",
                color="BRIGHT_BLUE",
            )
        else:
            if not self.settings.imagen_model_names:
                self.console_messenger.info(
                    "No Imagen models configured in .env. Cover generation will be skipped.",
                    color="YELLOW",
                )
            else:
                cover_current_model = self._select_model_interaktywnie(
                    model_type="Imagen (for Cover)",
                    available_models=self.settings.imagen_model_names,
                    default_index=0,
                )

        page_current_model: Optional[str] = None
        page_model_from_args: Optional[str] = args.page_imagen_model

        if (
            page_model_from_args
            and page_model_from_args != "?"
            and page_model_from_args in self.settings.imagen_model_names
        ):
            page_current_model = page_model_from_args
            self.console_messenger.info(
                f"Page Imagen model selected from arguments: '{page_current_model}'",
                color="BRIGHT_BLUE",
            )
        else:
            if not self.settings.imagen_model_names:
                self.console_messenger.info(
                    "No Imagen models configured in .env. Page generation will be skipped.",
                    color="YELLOW",
                )
            else:
                page_current_model = self._select_model_interaktywnie(
                    model_type="Imagen (for Pages)",
                    available_models=self.settings.imagen_model_names,
                    default_index=0,
                )

        genai_text_integration: GenAIIntegration = GenAIIntegration(
            api_key=self.settings.genai_api_key,
            model_name=genai_current_model,
            console_messenger=self.console_messenger,
        )
        self.stats_manager.record_model_usage("text_generation", genai_current_model)

        cover_imagen_integration: Optional[ImagenIntegration] = None
        if cover_current_model:
            try:
                self.console_messenger.info(
                    f"Initializing Imagen integration for Covers with model '{cover_current_model}'...",
                    color="BRIGHT_BLUE",
                )
                cover_imagen_integration = ImagenIntegration(
                    project_id=self.settings.gcp_project_id,
                    location=self.settings.gcp_location,
                    model_name=cover_current_model,
                    max_attempts=self.settings.max_generation_attempts,
                )
                self.stats_manager.record_model_usage(
                    "image_generation_cover", cover_current_model
                )
            except Exception as e:
                self.console_messenger.error(
                    f"Failed to initialize Cover Imagen integration with model '{cover_current_model}': {e}"
                )

        page_imagen_integration: Optional[ImagenIntegration] = None
        if page_current_model:
            try:
                self.console_messenger.info(
                    f"Initializing Imagen integration for Pages with model '{page_current_model}'...",
                    color="BRIGHT_BLUE",
                )
                page_imagen_integration = ImagenIntegration(
                    project_id=self.settings.gcp_project_id,
                    location=self.settings.gcp_location,
                    model_name=page_current_model,
                    max_attempts=self.settings.max_generation_attempts,
                )
                self.stats_manager.record_model_usage(
                    "image_generation_page", page_current_model
                )
            except Exception as e:
                self.console_messenger.error(
                    f"Failed to initialize Page Imagen integration with model '{page_current_model}': {e}"
                )

        return (
            args,
            genai_text_integration,
            cover_imagen_integration,
            page_imagen_integration,
        )
