from typing import Dict, Any, List
from celery import chord
from backend.app.schemas.color_book.coloring_book_project import ColoringBookProject
from backend.app.schemas.common.ai_preferences import AIPreferences

class ColorBookOrchestrator:
    """Główny orkiestrator zarządzający cyklem życia projektu kolorowanki."""
    
    def __init__(self, idea: str, preferences: AIPreferences):
        self.idea = idea
        self.preferences = preferences

    def start(self):
        """Uruchamia proces orkiestracji (Inicjalizacja -> Generowanie -> Finalizacja)."""
        # Tu logika wywoływania zadań Celery importowanych wewnątrz metod aby uniknąć cykli
        from backend.app.tasks.color_book import init_color_book_project
        
        # Wywołujemy pierwszy krok (sync/async zależnie od potrzeb)
        # To jest uproszczony schemat
        pass

    def create_generation_chord(self, project_data: Dict[str, Any]):
        """Tworzy strukturę Chord dla równoległego generowania stron."""
        from backend.app.tasks.color_book import generate_color_book_page, finalize_color_book
        
        pages = project_data.get("coloringBook", {}).get("mainProjectDetails", {}).get("pageIdeas", [])
        preferences_dict = self.preferences.model_dump()
        
        header_tasks = [
            generate_color_book_page.s(page, project_data, preferences_dict) 
            for page in pages
        ]
        
        callback = finalize_color_book.s(project_data)
        return chord(header_tasks)(callback)
