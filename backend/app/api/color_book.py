from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from backend.app.celery_app import celery_app
from backend.app.schemas.common.ai_preferences import AIPreferences
from pydantic import BaseModel

router = APIRouter(prefix="/color-book", tags=["color-book"])

class IdeaRequest(BaseModel):
    idea: Optional[str] = None
    page_limit: int = 40
    preferences: AIPreferences = AIPreferences()

class OrchestrateRequest(BaseModel):
    idea: str
    preferences: AIPreferences = AIPreferences()

@router.post("/init")
async def init_project(request: IdeaRequest):
    """
    Inicjalizuje projekt kolorowanki (generuje strukturę JSON).
    """
    task = celery_app.send_task(
        "color_book.init_project",
        args=[request.idea, request.preferences.model_dump()]
    )
    return {"task_id": task.id}

@router.post("/orchestrate")
async def start_orchestration(request: OrchestrateRequest):
    """
    Uruchamia pełny proces generowania kolorowanki.
    """
    task = celery_app.send_task(
        "color_book.orchestrate",
        args=[request.idea, request.preferences.model_dump()]
    )
    return {"task_id": task.id}

from backend.app.engine.color_book.project_store import ColorBookProjectStore

@router.get("/projects")
async def list_projects():
    """Zwraca listę projektów."""
    store = ColorBookProjectStore()
    return {"projects": store.list_projects()}

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Zwraca szczegóły projektu i listę plików."""
    store = ColorBookProjectStore()
    data = store.get_project_data(project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Project not found")
    files = store.list_project_files(project_id)
    return {"data": data, "files": files}

@router.post("/regenerate-page")
async def regenerate_page(project_id: str, page_number: int, preferences: AIPreferences = AIPreferences()):
    """Uruchamia ponowne generowanie pojedynczej strony."""
    store = ColorBookProjectStore()
    project_data = store.get_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Znajdź dane strony w JSONie
    pages = project_data.get("coloringBook", {}).get("mainProjectDetails", {}).get("pageIdeas", [])
    page_data = next((p for p in pages if p["pageNumber"] == page_number), None)
    
    if not page_data:
        raise HTTPException(status_code=404, detail=f"Page {page_number} not found in project")
        
    task = celery_app.send_task(
        "color_book.generate_page",
        args=[page_data, project_data, preferences.model_dump()]
    )
    return {"task_id": task.id}

@router.post("/regenerate-cover")
async def regenerate_cover(project_id: str, cover_type: str = "full_text", lang_code: Optional[str] = "en", preferences: AIPreferences = AIPreferences()):
    """Uruchamia ponowne generowanie okładki."""
    store = ColorBookProjectStore()
    project_data = store.get_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Zadanie Celery dla okładki (używamy generycznego zadania AI lub dedykowanego)
    # Na razie uproszczone wywołanie podobne do orchestrate ale tylko dla okładki
    task = celery_app.send_task(
        "color_book.generate_cover", # Muszę upewnić się że to zadanie istnieje w tasks/color_book.py
        args=[project_data, cover_type, lang_code, preferences.model_dump()]
    )
    return {"task_id": task.id}
