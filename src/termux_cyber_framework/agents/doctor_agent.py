import os
import json
import shutil
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel
from .config_manager_agent import ConfigManagerAgent

class DoctorAgent:
    """
    An agent responsible for running health checks on the system and attempting
    to self-heal from common configuration issues.
    """
    def __init__(self, logger: LoggerPort, config_manager: ConfigManagerAgent, config_paths: list[str], tool_catalog_path: str):
        self.logger = logger
        self.config_manager = config_manager
        self.config_paths = config_paths
        self.tool_catalog_path = tool_catalog_path

    def run_checks(self):
        """
        Runs all health checks and logs the results. Attempts to restore
        configs if they are invalid.
        """
        self.logger.log("Starting system health checks...", level=LogLevel.INFO)

        try:
            self._check_config_integrity()
            self._check_api_key()
            self._check_tool_availability()

            # If all checks passed, we can create backups of the good configs.
            self.backup_configs()

        except (FileNotFoundError, ValueError) as e:
            self.logger.log(f"A critical health check failed and could not be resolved: {e}", level=LogLevel.ERROR)
            raise

        self.logger.log("System health checks passed successfully.", level=LogLevel.INFO)

    def _is_config_valid(self, path: str) -> bool:
        """Helper to check if a single config file exists and is valid JSON."""
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError:
            return False

    def _restore_config(self, path: str) -> bool:
        """Attempts to restore a config file from its backup."""
        backup_path = f"{path}.bak"
        self.logger.log(f"Attempting to restore '{path}' from backup '{backup_path}'...", level=LogLevel.WARNING)
        if os.path.exists(backup_path):
            try:
                shutil.copy(backup_path, path)
                self.logger.log(f"Successfully restored '{path}'.", level=LogLevel.INFO)
                return True
            except Exception as e:
                self.logger.log(f"Failed to restore '{path}' from backup. Error: {e}", level=LogLevel.ERROR)
                return False
        else:
            self.logger.log(f"Backup file '{backup_path}' not found. Cannot restore.", level=LogLevel.ERROR)
            return False

    def _check_config_integrity(self):
        """
        Checks if config files are valid. If not, attempts to restore them
        from backup before failing.
        """
        self.logger.log("Checking configuration file integrity...", level=LogLevel.DEBUG)
        for path in self.config_paths:
            if not self._is_config_valid(path):
                self.logger.log(f"Configuration file '{path}' is missing or corrupt.", level=LogLevel.WARNING)
                if not self._restore_config(path) or not self._is_config_valid(path):
                    # If restore fails or the restored file is also invalid, raise an error.
                    raise ValueError(f"Critical configuration file '{path}' is corrupt or missing and could not be restored.")
        self.logger.log("Configuration files are valid.", level=LogLevel.DEBUG)

    def backup_configs(self):
        """Creates a backup of all critical configuration files."""
        self.logger.log("Backing up configuration files...", level=LogLevel.DEBUG)
        for path in self.config_paths:
            backup_path = f"{path}.bak"
            try:
                shutil.copy(path, backup_path)
            except Exception as e:
                self.logger.log(f"Failed to create backup for '{path}'. Error: {e}", level=LogLevel.WARNING)

    def _check_api_key(self):
        """Checks if a Google API key is configured via file or environment variable."""
        self.logger.log("Checking for Google API key...", level=LogLevel.DEBUG)
        key_from_config = self.config_manager.get_api_key('google_gemini')
        key_from_env = os.getenv("GOOGLE_API_KEY")

        if not key_from_config and not key_from_env:
            self.logger.log("Google API key is not set in config.json or as an environment variable. AI features will be unavailable.", level=LogLevel.WARNING)
        else:
            self.logger.log("Google API key is configured.", level=LogLevel.DEBUG)

    def _check_tool_availability(self):
        """Checks if tools listed in the catalog are available on the system PATH."""
        self.logger.log("Checking for tool availability...", level=LogLevel.DEBUG)
        try:
            with open(self.tool_catalog_path, 'r') as f:
                tools = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.log(f"Could not read tool catalog at '{self.tool_catalog_path}'. Skipping tool availability check. Error: {e}", level=LogLevel.WARNING)
            return

        missing_tools = []
        for tool_data in tools:
            command_to_check = (tool_data.get('run_command') or '').split(' ')[0]
            install_info = tool_data.get('install_info', {})
            if command_to_check and install_info.get('method') != 'git' and not shutil.which(command_to_check):
                 missing_tools.append(tool_data['name'])

        if missing_tools:
            self.logger.log(f"The following tools are not on the PATH and may need installation: {', '.join(missing_tools)}.", level=LogLevel.WARNING)
        else:
            self.logger.log("All non-Git-based tools in the catalog appear to be available on the PATH.", level=LogLevel.DEBUG)
