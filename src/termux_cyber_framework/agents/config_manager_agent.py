import json
import os
from typing import Optional

class ConfigManagerAgent:
    """
    Manages reading from and writing to the framework's configuration file.
    """
    def __init__(self, config_path: str = 'config/config.json'):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        """Loads the configuration from the file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                # If the file doesn't exist, start with a default structure.
                self.config = {"api_keys": {}}
        except (json.JSONDecodeError, IOError):
            # If file is corrupt or unreadable, start fresh
            self.config = {"api_keys": {}}

    def _save_config(self):
        """Saves the current configuration to the file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_api_key(self, service_name: str) -> Optional[str]:
        """
        Retrieves an API key for a given service.

        Args:
            service_name: The name of the service (e.g., 'google_gemini').

        Returns:
            The API key as a string, or None if not found.
        """
        return self.config.get("api_keys", {}).get(service_name)

    def set_api_key(self, service_name: str, api_key: str):
        """
        Sets and saves an API key for a given service.

        Args:
            service_name: The name of the service (e.g., 'google_gemini').
            api_key: The API key to save.
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][service_name] = api_key
        self._save_config()
