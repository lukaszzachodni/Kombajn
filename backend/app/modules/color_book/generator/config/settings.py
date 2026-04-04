import os
from dotenv import load_dotenv


class Settings:
    def __init__(self) -> None:
        load_dotenv()

        self.genai_api_key: str | None = os.getenv("GENAI_API_KEY")
        genai_models_str: str = os.getenv(
            "GENAI_MODEL_NAMES", "gemini-1.5-flash-latest,gemini-1.0-pro-latest"
        )
        self.genai_model_names: list[str] = [
            m.strip() for m in genai_models_str.split(",") if m.strip()
        ]
        self.genai_model_default: str | None = os.getenv("GENAI_MODEL_DEFAULT")

        self.gcp_project_id: str | None = os.getenv("GCP_PROJECT_ID")
        self.gcp_location: str = os.getenv("GCP_LOCATION", "us-central1")
        imagen_models_str: str = os.getenv("IMAGEN_MODEL_NAMES", "imagegeneration@006")
        self.imagen_model_names: list[str] = [
            m.strip() for m in imagen_models_str.split(",") if m.strip()
        ]
        self.imagen_cover_model_default: str | None = os.getenv("IMAGEN_COVER_MODEL_DEFAULT")
        self.imagen_page_model_default: str | None = os.getenv("IMAGEN_PAGE_MODEL_DEFAULT")

        self.max_generation_attempts: int = int(os.getenv("MAX_GENERATION_ATTEMPTS", 2))
        self.page_limit: int = int(os.getenv("PAGE_LIMIT", 40))
        self.cover_variants_per_prompt: int = int(os.getenv("COVER_VARIANTS_PER_PROMPT", 1))
        self.page_variants_per_prompt: int = int(os.getenv("PAGE_VARIANTS_PER_PROMPT", 1))

        cover_types_str: str = os.getenv("COVER_GENERATION_TYPES", "full_text,blank_title,no_text")
        self.cover_generation_types: list[str] = [
            t.strip() for t in cover_types_str.split(",") if t.strip()
        ]

        self.stats_filename: str = os.getenv("STATS_FILENAME", "run_statistics.json")

        self.output_dir: str = os.getenv("OUTPUT_DIR", "generated_projects")
        self.project_scheme_path: str = os.getenv(
            "PROJECT_SCHEME_PATH", "schemes/project_scheme.json"
        )
        self.prompts_path: str = os.getenv("PROMPTS_PATH", "src/config/prompts.json")

        self._validate_settings()

    def _validate_settings(self) -> None:
        if not self.genai_api_key or self.genai_api_key == "YOUR_GENAI_API_KEY":
            raise ValueError(
                "GENAI_API_KEY is not set or is still a placeholder. "
                "Please set it in your .env file."
            )
        if not self.genai_model_names:
            raise ValueError(
                "No GENAI_MODEL_NAMES specified in .env. "
                "Please provide at least one (e.g., GENAI_MODEL_NAMES=gemini-1.5-flash-latest)."
            )
        if not self.imagen_model_names:
            print(
                "Warning: No IMAGEN_MODEL_NAMES specified in .env. Image generation with Imagen might fail. "
                "Please provide at least one (e.g., IMAGEN_MODEL_NAMES=imagegeneration@006)."
            )
        if not self.gcp_project_id or self.gcp_project_id == "YOUR_GCP_PROJECT_ID":
            print(
                "Warning: GCP_PROJECT_ID is not set or is still a placeholder. "
                "Image generation with Imagen might fail. Set it in your .env file."
            )