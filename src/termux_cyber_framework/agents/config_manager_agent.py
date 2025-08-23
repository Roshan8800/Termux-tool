import json
from typing import Optional
from .file_manager_agent import FileManagerAgent

class ConfigManagerAgent:
    """
    Manages reading from and writing to the framework's configuration file
    using the FileManagerAgent.
    """
    def __init__(self, file_manager: FileManagerAgent, config_path: str = 'config/config.json'):
        self.file_manager = file_manager
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        """Loads the configuration from the file."""
        if self.file_manager.path_exists(self.config_path):
            content = self.file_manager.read_file(self.config_path)
            try:
                self.config = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                # If content is None or corrupt
                self.config = {"api_keys": {}}
        else:
            self.config = {"api_keys": {}}

    def _save_config(self):
        """Saves the current configuration to the file."""
        content = json.dumps(self.config, indent=2)
        self.file_manager.write_file(self.config_path, content)

    def get_api_key(self, service_name: str) -> Optional[str]:
        """
        Retrieves an API key for a given service.
        """
        return self.config.get("api_keys", {}).get(service_name)

    def set_api_key(self, service_name: str, api_key: str):
        """
        Sets and saves an API key for a given service.
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][service_name] = api_key
        self._save_config()
