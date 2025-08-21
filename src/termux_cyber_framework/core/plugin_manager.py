import os
import importlib
import inspect
from typing import Dict
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.use_cases.ports import LoggerPort

class PluginManager:
    def __init__(self, plugin_dir="src/termux_cyber_framework/adapters/plugins", config: Config = None, command_runner: CommandRunner = None, logger: LoggerPort = None):
        self.plugin_dir = plugin_dir
        self.config = config or Config()
        self.command_runner = command_runner or CommandRunner()
        self.logger = logger

    def load_plugins(self) -> Dict[str, ToolAdapterPort]:
        adapters = {}
        plugin_path = self.plugin_dir.replace("/", ".")
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"{plugin_path}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, ToolAdapterPort) and obj is not ToolAdapterPort:
                            adapter_instance = obj(config=self.config, command_runner=self.command_runner, logger=self.logger)
                            tool = adapter_instance.find_tool()
                            if tool:
                                adapters[tool.name] = adapter_instance
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")
        return adapters
