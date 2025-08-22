import os
import json
import importlib
from typing import Dict, List
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort, LoggerPort, LogLevel, InstallerStrategyPort
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.models import Tool, InstallInfo
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.adapters.plugins.generic_adapter import GenericToolAdapter

class PluginManager:
    def __init__(self, config: Config = None, command_runner: CommandRunner = None, logger: LoggerPort = None, installers: Dict[str, InstallerStrategyPort] = None):
        self.config = config or Config()
        self.command_runner = command_runner or CommandRunner()
        self.logger = logger
        self.installers = installers or {}
        self.tool_catalog_path = self._get_tool_catalog_path()

    def _get_tool_catalog_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "..", "..", "..", "data", "tool_catalog.json")

    def _load_tools_from_catalog(self) -> List[Tool]:
        try:
            with open(self.tool_catalog_path, 'r') as f:
                tools_data = json.load(f)

            tools = []
            for tool_data in tools_data:
                install_info = InstallInfo(**tool_data["install_info"])
                tool_data["install_info"] = install_info
                tools.append(Tool(**tool_data))
            return tools
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.log(f"Error loading tool catalog: {e}", level=LogLevel.ERROR)
            return []

    def load_plugins(self) -> Dict[str, ToolAdapterPort]:
        adapters = {}
        tools = self._load_tools_from_catalog()

        for tool in tools:
            if tool.adapter_class:
                try:
                    module_path, class_name = tool.adapter_class.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    adapter_class = getattr(module, class_name)
                    # This assumes a consistent constructor signature for specific adapters
                    adapters[tool.name] = adapter_class(config=self.config, command_runner=self.command_runner, logger=self.logger)
                except (ImportError, AttributeError, TypeError) as e:
                    self.logger.log(f"Failed to load adapter '{tool.adapter_class}' for tool '{tool.name}': {e}", level=LogLevel.ERROR)
            else:
                # Use the GenericToolAdapter for tools with no specific adapter class
                adapters[tool.name] = GenericToolAdapter(tool=tool, command_runner=self.command_runner, logger=self.logger, config=self.config)

        return adapters
