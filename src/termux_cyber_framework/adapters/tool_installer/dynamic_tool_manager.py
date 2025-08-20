import json
import os
import shutil
import subprocess
import importlib
from typing import List, Optional, Dict

from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import ToolInstallerPort, ToolRunnerPort

class DynamicToolManagerAdapter(ToolInstallerPort):
    """
    Manages tools and dynamically loads their adapters based on a JSON manifest.
    """
    def __init__(self, tools_manifest_path: str):
        self._tools = self._load_tools_from_manifest(tools_manifest_path)
        print(f"[*] Loaded {len(self._tools)} tools from manifest.")

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
        return shutil.which(tool.run_command) is not None

    def install_tool(self, tool: Tool) -> bool:
        print(f"[*] Running installation command: '{tool.install_command}'")
        try:
            process = subprocess.run(
                tool.install_command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(process.stdout)
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"[-] Error installing tool {tool.name}: {e.stderr}")
            return False

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
