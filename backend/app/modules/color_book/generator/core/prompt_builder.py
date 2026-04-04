import json
from typing import Dict, List, Optional
from backend.app.modules.color_book.generator.utils.file_utils import FileUtils
from backend.app.modules.color_book.generator.config.settings import Settings


class PromptBuilder:
    """
    Builds prompts for GenAI and Imagen models.
    Separates business logic (prompt structure) from API communication.
    """

    def __init__(self) -> None:
        self.settings: Settings = Settings()
        self.prompts: Dict = self._load_prompts(self.settings.prompts_path)

    def _load_prompts(self, prompts_path: str) -> Dict:
        """
        Loads prompts from a JSON file.
        """
        prompts_data: Optional[Dict] = FileUtils.read_json(prompts_path)
        if not prompts_data:
            raise RuntimeError(f"Could not load prompts from {prompts_path}")
        return prompts_data

    def _get_common_project_context(self, genai_project_data: Dict) -> Dict:
        """
        Retrieves key, common project information.
        """
        main_details: Dict = genai_project_data.get("coloringBook", {}).get(
            "mainProjectDetails", {}
        )

        art_style_guidance: str = "cartoon, kid-friendly, simple, whimsical, line art"
        if isinstance(main_details.get("artStyleGuidance"), list):
            additional_styles: List[str] = [
                style
                for style in main_details["artStyleGuidance"]
                if style not in art_style_guidance
            ]
            if additional_styles:
                art_style_guidance += ", " + ", ".join(additional_styles)
        elif isinstance(main_details.get("artStyleGuidance"), str):
            if main_details["artStyleGuidance"] not in art_style_guidance:
                art_style_guidance += ", " + main_details["artStyleGuidance"]

        return {
            "book_title": main_details.get("title", "Coloring Book"),
            "age_range": main_details.get("ageRange", "children"),
            "main_theme": main_details.get("mainTheme", "various subjects"),
            "creative_brief": main_details.get("creativeBrief", ""),
            "art_style_guidance": art_style_guidance,
            "coloring_page_guidelines": main_details.get(
                "coloringPageGuidelines",
                "Pure line art, black outlines on a white background. No fills or shading. Clear, distinct lines.",
            ),
        }

    def get_ai_theme_generation_prompt(self) -> str:
        """
        Builds a prompt for GenAI to generate a creative coloring book theme.
        """
        base_prompt_instruction: str = self.prompts["ai_theme_generation_prompt"][
            "prompt"
        ]

        final_prompt_dict: Dict = {
            "instruction_prompt": base_prompt_instruction,
        }
        return json.dumps(final_prompt_dict, indent=2, ensure_ascii=False)

    def build_project_generation_prompt(
        self,
        idea_prompt: str,
        scheme: Dict,
        page_limit: int,
    ) -> str:
        """
        Builds a prompt for the GenAI model to generate the coloring book project structure.
        """
        base_prompt_instruction: str = self.prompts["project_generation_prompt"][
            "prompt"
        ].format(page_limit=page_limit)

        dynamic_params: Dict = {
            "idea_prompt": idea_prompt,
            "scheme_json": json.dumps(scheme, indent=2, ensure_ascii=False),
            "page_limit": page_limit,
        }

        final_prompt_dict: Dict = {
            "instruction_prompt": base_prompt_instruction,
            "parameters_for_analysis": dynamic_params,
        }
        return json.dumps(final_prompt_dict, indent=2, ensure_ascii=False)

    def get_cover_generation_prompt(
        self, genai_project_data: Dict, cover_type: str, title: Optional[str] = None
    ) -> str:
        """
        Generates a prompt for the Imagen model to create a cover.
        """
        context: Dict = self._get_common_project_context(genai_project_data)
        cover_details: Dict = (
            genai_project_data.get("coloringBook", {})
            .get("mainProjectDetails", {})
            .get("coverDetails", {})
        )

        book_title: str = title if title else context["book_title"]

        scene_description: str = cover_details.get(
            "sceneDescription",
            "A cheerful and inviting scene suitable for a children's coloring book cover.",
        )
        graphic_style: str = cover_details.get("graphicStyle", "vibrant cartoon style")

        base_prompt_instruction: str
        if cover_type == "full_text":
            base_prompt_instruction = self.prompts["cover_generation_prompt"][
                "full_text"
            ].format(
                book_title=book_title,
                scene_description=scene_description,
                graphic_style=graphic_style,
                art_style_guidance=context["art_style_guidance"],
                aspect_ratio="3:4",
            )
        elif cover_type == "blank_title":
            base_prompt_instruction = self.prompts["cover_generation_prompt"][
                "blank_title"
            ].format(
                scene_description=scene_description,
                graphic_style=graphic_style,
                art_style_guidance=context["art_style_guidance"],
                aspect_ratio="3:4",
            )
        elif cover_type == "no_text":
            base_prompt_instruction = self.prompts["cover_generation_prompt"][
                "no_text"
            ].format(
                scene_description=scene_description,
                graphic_style=graphic_style,
                art_style_guidance=context["art_style_guidance"],
                aspect_ratio="3:4",
            )
        else:
            raise ValueError(f"Unknown cover type: {cover_type}")

        final_prompt_dict: Dict = {
            "instruction_prompt": base_prompt_instruction,
        }
        return json.dumps(final_prompt_dict, indent=2, ensure_ascii=False)

    def get_page_generation_prompt(
        self,
        page_idea_entry: Dict,
        genai_project_data: Dict,
    ) -> str:
        """
        Generates a prompt for the Imagen model to create a single coloring book page.
        """
        context: Dict = self._get_common_project_context(genai_project_data)

        prompt_reference_id: Optional[str] = page_idea_entry.get("promptReferenceId")
        if not prompt_reference_id:
            raise ValueError(
                f"Missing 'promptReferenceId' in page_idea_entry: {page_idea_entry}"
            )

        page_prompt_library: List[Dict] = genai_project_data.get(
            "coloringBook", {}
        ).get("pagePromptLibrary", [])
        page_details_from_library: Optional[Dict] = next(
            (
                item
                for item in page_prompt_library
                if item.get("promptId") == prompt_reference_id
            ),
            None,
        )

        if not page_details_from_library:
            raise ValueError(
                f"Page details not found for promptReferenceId: {prompt_reference_id}"
            )

        page_number: str = page_idea_entry.get("pageNumber", "N/A")
        scene_description: str = page_details_from_library.get(
            "sceneDescription", "A simple scene for coloring."
        )
        graphic_style: str = page_details_from_library.get(
            "graphicStyle", "cartoon line art"
        )
        emotional_tone: str = page_details_from_library.get("emotionalTone", "neutral")
        complexity_level: str = page_details_from_library.get(
            "complexityLevel", "simple"
        )

        base_prompt_instruction: str = self.prompts["page_generation_prompt"][
            "prompt"
        ].format(
            book_title=context["book_title"],
            main_theme=context["main_theme"],
            creative_brief=context["creative_brief"],
            page_number=page_number,
            scene_description=scene_description,
            graphic_style=graphic_style,
            emotional_tone=emotional_tone,
            complexity_level=complexity_level,
        )

        final_prompt_dict: Dict = {
            "instruction_prompt": base_prompt_instruction,
        }
        return json.dumps(final_prompt_dict, indent=2, ensure_ascii=False)
