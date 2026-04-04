from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.app.modules.color_book.generator.config.settings import Settings
from backend.app.modules.color_book.generator.core.genai_integration import GenAIIntegration
from backend.app.modules.color_book.generator.core.project_manager import ProjectManager
from backend.app.modules.color_book.generator.core.prompt_builder import PromptBuilder
from backend.app.modules.color_book.generator.core.statistics_manager import StatisticsManager
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger
from backend.app.modules.color_book.generator.core.genai_project_generator import GenAIProjectGenerator
from backend.app.modules.color_book.generator.utils.file_utils import FileUtils

router = APIRouter(prefix="/color-book", tags=["color-book"])

class IdeaRequest(BaseModel):
    idea: Optional[str] = None
    page_limit: int = 40

class MockArgs:
    def __init__(self, idea=None):
        self.idea = idea
        self.genai_model = None
        self.cover_imagen_model = None
        self.page_imagen_model = None
        self.cover_variants = None
        self.page_variants = None
        self.cover_types = None
        self.regenerate = False

@router.post("/idea")
async def generate_idea(request: IdeaRequest):
    """
    Generates a coloring book idea (theme, titles, and page descriptions) using GenAI.
    """
    settings = Settings()
    console_messenger = ConsoleMessenger()
    stats_manager = StatisticsManager(settings.output_dir, settings.stats_filename)
    project_manager = ProjectManager(settings.output_dir)
    prompt_builder = PromptBuilder()
    
    # Mocking arguments for the generator
    args = MockArgs(idea=request.idea)
    
    # Initialize GenAI Integration
    genai_model = settings.genai_model_default or settings.genai_model_names[0]
    genai_integration = GenAIIntegration(
        api_key=settings.genai_api_key,
        model_name=genai_model,
        console_messenger=console_messenger
    )
    
    # We don't need Imagen for just generating the idea/structure
    imagen_integration = None 
    
    generator = GenAIProjectGenerator(
        genai_integration=genai_integration,
        prompt_builder=prompt_builder,
        project_manager=project_manager,
        stats_manager=stats_manager,
        settings=settings,
        args=args,
        console_messenger=console_messenger,
        imagen_integration=imagen_integration
    )
    
    try:
        scheme = FileUtils.read_json(settings.project_scheme_path)
        if not scheme:
            raise HTTPException(status_code=500, detail="Could not read project scheme.")
            
        project_data, project_folder = generator.generate_project_data(scheme, request.page_limit)
        
        if not project_data:
            raise HTTPException(status_code=500, detail="Failed to generate project data.")
            
        return {
            "status": "success",
            "project_folder": project_folder,
            "project_data": project_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
