import os
import json
from backend.app.modules.color_book.binding.data_models.project_schema import validate_project_data

class ProjectDataLoader:
    def __init__(self, messenger):
        self.messenger = messenger

    def load_and_validate_project_data(self, dir_path, project_name):
        project_data_path = os.path.join(dir_path, "project_data.json")
        project_data = {}
        if os.path.exists(project_data_path):
            try:
                with open(project_data_path, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                is_valid, error_message = validate_project_data(project_data)
                if not is_valid:
                    self.messenger.error(
                        f"Error: project_data.json for {project_name} is invalid: {error_message}"
                    )
                    return None
            except json.JSONDecodeError as e:
                self.messenger.error(
                    f"Error decoding project_data.json for {project_name}: {e}"
                )
                return None
        else:
            self.messenger.error(
                f"Error: project_data.json not found for {project_name}. Aborting project processing."
            )
            return None
        return project_data
