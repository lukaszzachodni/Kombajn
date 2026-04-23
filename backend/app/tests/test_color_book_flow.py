import pytest
import os
import shutil
from backend.app.schemas.common.ai_preferences import AIPreferences
from backend.app.tasks.color_book import init_color_book_project, generate_color_book_page, finalize_color_book

def test_full_color_book_flow_mock():
    """Testuje pełny przepływ kolorowanki używając mocków."""
    
    preferences = AIPreferences(llm_provider="mock", image_gen_provider="mock")
    pref_dict = preferences.model_dump()
    
    # 1. Inicjalizacja projektu
    idea = "Cats in space"
    project_data = init_color_book_project(idea, pref_dict)
    
    assert project_data["title"] == "Mock Coloring Book"
    
    # 2. Generowanie pojedynczej strony (mock)
    page_data = {"pageNumber": 1, "sceneDescription": "A cat on the moon"}
    img_path = generate_color_book_page(page_data, project_data, pref_dict)
    
    assert img_path == "path/to/page.png"
    
    # 3. Finalizacja (składanie)
    tmp_img_dir = "data/tests/tmp_images"
    os.makedirs(tmp_img_dir, exist_ok=True)
    fake_img = os.path.join(tmp_img_dir, "page_1.png")
    
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color = (255, 255, 255))
    img.save(fake_img)
        
    results = [fake_img]
    final_paths = finalize_color_book(results, project_data)
    
    assert "manuscript" in final_paths
    assert "excel" in final_paths
    assert os.path.exists(final_paths["manuscript"])
    
    # Cleanup
    shutil.rmtree("data/projects/tmp_project", ignore_errors=True)
    shutil.rmtree(tmp_img_dir, ignore_errors=True)
