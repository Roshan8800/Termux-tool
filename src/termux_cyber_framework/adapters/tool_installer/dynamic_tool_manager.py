import json
import os
import shutil
import importlib
from typing import List, Optional, Dict

from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import (
    ToolInstallerPort, ToolRunnerPort, InstallerStrategyPort
)
from termux_cyber_framework.core.command_runner import CommandRunner
from .git_installer import GitInstallerAdapter
from .pip_installer import PipInstallerAdapter
from .pkg_installer import PkgInstallerAdapter

class DynamicToolManagerAdapter(ToolInstallerPort):
    """
    Manages tools by delegating installation to specific strategy adapters
    and dynamically loading tool runner adapters based on a JSON manifest.
    """
    def __init__(self, tools_manifest_path: str, command_runner: Optional[CommandRunner] = None):
        self._tools = self._load_tools_from_manifest(tools_manifest_path)
        command_runner = command_runner or CommandRunner()
        self._installers: Dict[str, InstallerStrategyPort] = {
            "git": GitInstallerAdapter(command_runner),
            "pip": PipInstallerAdapter(command_runner),
            "pkg": PkgInstallerAdapter(command_runner),
        }
        print(f"[*] Loaded {len(self._tools)} tools from manifest.")
        print(f"[*] Registered {len(self._installers)} installation methods: {list(self._installers.keys())}")

    def _load_tools_from_manifest(self, path: str) -> List[Tool]:
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            tool_data = json.load(f)
            return [Tool(**data) for data in tool_data]

    def find_tool(self, name: str) -> Optional[Tool]:
        for tool in self._tools:
            if tool.name.lower() == name.lower():
                return tool
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        """
        Delegates the installation check to the appropriate strategy adapter.
        """
        method = tool.install_info.method
        installer = self._installers.get(method)

        if not installer:
            print(f"[-] No installer found for method '{method}'.")
            return False

        return installer.is_installed(tool)

    def install_tool(self, tool: Tool) -> bool:
        """
        Delegates the installation of a tool to the appropriate strategy adapter.
        """
        method = tool.install_info.method
        installer = self._installers.get(method)

        if not installer:
            print(f"[-] No installer found for method '{method}'.")
            return False

        print(f"[*] Using '{method}' installer for tool '{tool.name}'.")
        return installer.install(tool)

    def load_tool_runners(self) -> Dict[str, ToolRunnerPort]:
        """
        Dynamically loads and instantiates tool runner adapters from the manifest.
        """
        runners = {}
        for tool in self._tools:
            if tool.adapter_class:
                try:
                    module_path, class_name = tool.adapter_class.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    adapter_class = getattr(module, class_name)
                    runners[tool.name.lower()] = adapter_class()
                    print(f"[*] Dynamically loaded adapter '{class_name}' for tool '{tool.name}'.")
                except (ImportError, AttributeError) as e:
                    print(f"[-] Warning: Could not load adapter for '{tool.name}': {e}")
        return runners
