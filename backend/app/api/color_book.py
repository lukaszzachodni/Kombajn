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
