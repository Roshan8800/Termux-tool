import json
from typing import List, Dict, Any, Optional

from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.core.domain.models import Tool

class DoctorAgent:
    """
    Performs user-facing health checks on the framework's configuration and dependencies.
    """
    def __init__(
        self,
        tool_installer: ToolInstallerAgent,
        config_manager: ConfigManagerAgent,
        master_interpreter: MasterAIInterpreter,
        tool_catalog_path: str = "data/tool_catalog.json"
    ):
        self._tool_installer = tool_installer
        self._config_manager = config_manager
        self._master_interpreter = master_interpreter
        self._tool_catalog_path = tool_catalog_path
        self._tool_catalog = self._load_tool_catalog()

    def _load_tool_catalog(self) -> List[Dict[str, Any]]:
        """Loads the tool catalog from the JSON file."""
        try:
            with open(self._tool_catalog_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    async def run_health_checks(self) -> List[Dict[str, Any]]:
        """
        Runs a series of checks and returns a list of results for display.
        """
        checks = []

        # 1. Check for config file
        config_exists = self._config_manager.config_exists()
        checks.append({
            "check": "Configuration File",
            "status": "OK" if config_exists else "ERROR",
            "message": f"config.json found."
        })

        # 2. Check for API key
        api_key = self._config_manager.get_api_key("google_gemini")
        key_is_set = api_key and api_key != "dummy_key_for_testing"
        checks.append({
            "check": "Gemini API Key",
            "status": "OK" if key_is_set else "WARN",
            "message": "API key is configured." if key_is_set else "Not set. Will be requested on first use."
        })

        # 3. Validate API key connectivity
        if key_is_set:
            is_valid = await self._master_interpreter._validate_api_key(api_key)
            checks.append({
                "check": "Gemini API Connectivity",
                "status": "OK" if is_valid else "ERROR",
                "message": "Successfully connected to the Gemini API." if is_valid else "Failed to connect with the configured key."
            })

        # 4. Check all tools in the catalog
        if not self._tool_catalog:
             checks.append({"check": "Tool Catalog", "status": "ERROR", "message": "tool_catalog.json is missing or invalid."})
        else:
            for tool_data in self._tool_catalog:
                try:
                    tool = Tool(**tool_data)
                    is_installed = self._tool_installer.is_installed(tool)
                    checks.append({
                        "check": f"Tool: {tool.name}",
                        "status": "OK" if is_installed else "INFO",
                        "message": "Installed" if is_installed else "Not installed (will be installed on-demand)."
                    })
                except Exception:
                    # Catches Pydantic validation errors for malformed entries
                    checks.append({
                        "check": f"Tool: {tool_data.get('name', 'N/A')}",
                        "status": "ERROR",
                        "message": "Invalid tool definition in catalog."
                    })

        return checks
