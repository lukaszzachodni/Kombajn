import os
import shutil
from typing import Optional

from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class ProjectManager:
    """
    Manages project-related file operations, including folder creation,
    saving images, configuration files, and general text files.
    """

    def __init__(self, output_base_dir: str = "output") -> None:
        self.output_base_dir: str = output_base_dir
        os.makedirs(self.output_base_dir, exist_ok=True)
        ConsoleMessenger.info(
            f"ProjectManager initialized. Output directory: {self.output_base_dir}"
        )

    def create_project_folder(self, project_name: str) -> Optional[str]:
        """
        Creates a folder for a new project.
        """
        project_path: str = os.path.join(self.output_base_dir, project_name).replace(
            ":", "-"
        )
        try:
            os.makedirs(project_path, exist_ok=True)
            return project_path
        except OSError as e:
            ConsoleMessenger.error(f"Error creating project folder {project_path}: {e}")
            return None

    def save_image(
        self, project_folder: str, image_name: str, image_data: bytes
    ) -> None:
        """
        Saves image data (bytes) to a PNG file in the project folder.
        """
        file_path: str = os.path.join(project_folder, f"{image_name}.png")
        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
            ConsoleMessenger.info(f"Image saved to {file_path}")
        except IOError as e:
            ConsoleMessenger.error(f"Error saving image to {file_path}: {e}")

    def save_config_file(
        self, project_folder: str, config_file_path: str, new_name: Optional[str] = None
    ) -> None:
        """
        Copies the configuration file to the project folder.
        """
        if not os.path.exists(config_file_path):
            ConsoleMessenger.warning(
                f"Warning: Configuration file not found at {config_file_path}. Skipping save."
            )
            return

        file_name: str = new_name if new_name else os.path.basename(config_file_path)
        destination_path: str = os.path.join(project_folder, file_name)
        try:
            shutil.copy2(config_file_path, destination_path)
            ConsoleMessenger.info(
                f"Copied config file '{os.path.basename(config_file_path)}' to {destination_path}"
            )
        except IOError as e:
            ConsoleMessenger.error(
                f"Error copying config file {config_file_path} to {destination_path}: {e}"
            )

    def save_file(self, project_folder: str, file_name: str, file_content: str) -> None:
        """
        Saves generic text content to a file in the project folder and verifies its content.
        """
        file_path: str = os.path.join(project_folder, file_name)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            ConsoleMessenger.info(
                f"Attempted to save file to {file_path} with length {len(file_content)}"
            )

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f_read:
                    read_content: str = f_read.read()
                if read_content == file_content:
                    ConsoleMessenger.success(
                        f"File {file_path} saved and verified successfully."
                    )
                else:
                    ConsoleMessenger.error(
                        f"File {file_name} saved but content verification failed."
                    )
            else:
                ConsoleMessenger.error(
                    f"File {file_name} was not found after saving attempt."
                )

        except IOError as e:
            ConsoleMessenger.error(f"Error saving file to {file_path}: {e}")
