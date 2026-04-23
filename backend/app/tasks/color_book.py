import os
import json
from celery import shared_task, chord
from typing import Dict, Any, List
from backend.app.services.ai.factory import AIServiceFactory
from backend.app.schemas.color_book.coloring_book_project import ColoringBookProject
# Tu będą importy procesorów gdy je przeniesiemy

@shared_task(name="color_book.init_project")
def init_color_book_project(idea: str, preferences_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Inicjalizuje projekt kolorowanki używając LLM."""
    from backend.app.schemas.common.ai_preferences import AIPreferences
    preferences = AIPreferences(**preferences_dict)
    
    llm = AIServiceFactory.get_llm_provider(preferences)
    
    # Prompt powinien być pobierany z konfiguracji/pliku
    prompt = f"Act as an expert creator of coloring book projects. Generate a complete JSON for theme: {idea}."
    
    project_data = llm.generate_json(prompt)
    if not project_data:
        raise RuntimeError("Failed to generate project data via LLM")
        
    return project_data

@shared_task(name="color_book.generate_page")
def generate_color_book_page(page_data: Dict[str, Any], project_context: Dict[str, Any], preferences_dict: Dict[str, Any]) -> str:
    """Generuje pojedynczą stronę kolorowanki."""
    from backend.app.schemas.common.ai_preferences import AIPreferences
    preferences = AIPreferences(**preferences_dict)
    
    image_gen = AIServiceFactory.get_image_gen_provider(preferences)
    
    # Budowanie promptu na podstawie page_data i context
    prompt = f"Coloring page: {page_data.get('sceneDescription')}. Pure black and white line art."
    
    images = image_gen.generate_images(prompt, number_of_images=1, aspect_ratio="3:4")
    if not images:
        raise RuntimeError(f"Failed to generate image for page {page_data.get('pageNumber')}")
        
    # Zapisywanie obrazu do storage i zwracanie ścieżki
    # path = storage.save_image(images[0])
    return "path/to/page.png"

from backend.app.engine.color_book.manuscript_processor import ManuscriptProcessor
from backend.app.engine.color_book.cover_processor import CoverProcessor
from backend.app.engine.color_book.kdp_excel_processor import KDPExcelProcessor

@shared_task(name="color_book.finalize")
def finalize_color_book(results: List[str], project_data: Dict[str, Any]):
    """Zbiera wszystkie wygenerowane strony i składa finałowy PDF/Excel."""
    output_dir = os.path.join("data", "projects", project_data.get("id", "tmp_project"))
    
    # 1. Manuskrypt
    man_proc = ManuscriptProcessor(output_dir=output_dir)
    pdf_man_path = man_proc.generate(results)
    
    # 2. Excel KDP
    xls_proc = KDPExcelProcessor(output_dir=output_dir)
    xls_path = xls_proc.generate(project_data)
    
    return {"manuscript": pdf_man_path, "excel": xls_path}

@shared_task(name="color_book.orchestrate")
def orchestrate_color_book(idea: str, preferences_dict: Dict[str, Any]):
    """Główny orkiestrator zarządzający flow projektu."""
    from backend.app.schemas.common.ai_preferences import AIPreferences
    from backend.app.engine.color_book.orchestrator import ColorBookOrchestrator
    
    preferences = AIPreferences(**preferences_dict)
    
    # 1. Init (LLM)
    project_data = init_color_book_project(idea, preferences_dict)
    
    # 2. Start Orchestration
    orch = ColorBookOrchestrator(idea, preferences)
    return orch.create_generation_chord(project_data)
