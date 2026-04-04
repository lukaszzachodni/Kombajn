import os
import datetime
import json
from typing import Any, Dict, Optional

from backend.app.modules.color_book.generator.utils.file_utils import FileUtils
from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class StatisticsManager:
    """
    Manages the collection and saving of application statistics.
    """

    def __init__(self, output_dir: str, filename: str = "stats.json") -> None:
        self.output_dir: str = output_dir
        self.filename: str = filename
        self.stats: Dict[str, Any] = {
            "run_id": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "start_time": None,
            "end_time": None,
            "total_execution_time_seconds": None,
            "models_used": {},
            "generation_details": [],
        }
        self.current_event: Optional[Dict[str, Any]] = None

    def start_run(self) -> None:
        """
        Records the start time of the application run.
        """
        self.stats["start_time"] = datetime.datetime.now().isoformat()
        ConsoleMessenger.info(f"Statistics: Run started at {self.stats['start_time']}")

    def end_run(self) -> None:
        """
        Records the end time and calculates total execution time.
        """
        self.stats["end_time"] = datetime.datetime.now().isoformat()
        if self.stats["start_time"]:
            start: datetime.datetime = datetime.datetime.fromisoformat(
                self.stats["start_time"]
            )
            end: datetime.datetime = datetime.datetime.fromisoformat(
                self.stats["end_time"]
            )
            self.stats["total_execution_time_seconds"] = (end - start).total_seconds()
        ConsoleMessenger.info(f"Statistics: Run ended at {self.stats['end_time']}")
        ConsoleMessenger.info(
            f"Statistics: Total execution time: {self.stats['total_execution_time_seconds']:.2f} seconds"
        )

    def record_model_usage(self, model_type: str, model_name: str) -> None:
        """
        Records which AI models were used.
        """
        self.stats["models_used"][model_type] = model_name

    def start_event(
        self,
        event_name: str,
        event_type: str,
        prompt: Optional[str] = None,
        page_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Starts timing a specific event.
        """
        event_id: str = (
            f"{event_type}_{event_name}_{datetime.datetime.now().timestamp()}"
        )
        parsed_prompt: Any = prompt
        if (
            isinstance(prompt, str)
            and prompt.strip().startswith("{")
            and prompt.strip().endswith("}")
        ):
            try:
                parsed_prompt = json.loads(prompt)
            except json.JSONDecodeError:
                pass
        self.current_event = {
            "id": event_id,
            "name": event_name,
            "type": event_type,
            "start_time": datetime.datetime.now().isoformat(),
            "prompt": parsed_prompt,
            "page_number": page_number,
            "attempts": 0,
            "duration_seconds": None,
            "status": "in_progress",
        }
        return self.current_event

    def end_event(
        self,
        event_data: Dict[str, Any],
        status: str = "completed",
        attempts: int = 1,
        api_response: Any = None,
    ) -> None:
        """
        Ends timing a specific event and adds it to the statistics.
        """
        end_time: str = datetime.datetime.now().isoformat()
        event_data["end_time"] = end_time
        event_data["status"] = status
        event_data["attempts"] = attempts
        event_data["api_response"] = api_response

        start: datetime.datetime = datetime.datetime.fromisoformat(
            event_data["start_time"]
        )
        end: datetime.datetime = datetime.datetime.fromisoformat(event_data["end_time"])
        event_data["duration_seconds"] = (end - start).total_seconds()

        self.stats["generation_details"].append(event_data)
        ConsoleMessenger.info(
            f"Statistics: Event '{event_data['name']}' ({event_data['type']}) {status} in {event_data['duration_seconds']:.2f} seconds (attempts: {attempts})."
        )
        self.current_event = None

    def save_stats(self, project_folder: Optional[str] = None) -> None:
        """
        Saves the collected statistics to a JSON file.
        """
        target_directory: str = project_folder if project_folder else self.output_dir
        full_path: str = os.path.join(target_directory, self.filename)
        try:
            FileUtils.write_json(full_path, self.stats)
            ConsoleMessenger.info(f"Statistics saved to {full_path}")
        except IOError as e:
            ConsoleMessenger.error(f"Error saving statistics to {full_path}: {e}")
