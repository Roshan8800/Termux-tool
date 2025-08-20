import json
import os
import shutil
import subprocess
from typing import List, Optional

from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import ToolInstallerPort

class LocalToolInstallerAdapter(ToolInstallerPort):
    """
    Manages tool installation based on a local JSON manifest file.
    """
    def __init__(self, tools_manifest_path: str):
        self._tools = self._load_tools(tools_manifest_path)
        print(f"[*] Loaded {len(self._tools)} tools from manifest.")

    def _load_tools(self, path: str) -> List[Tool]:
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            tool_data = json.load(f)
            return [Tool(**data) for data in tool_data]

    def find_tool(self, name: str) -> Optional[Tool]:
        """Finds a tool by name (case-insensitive)."""
        for tool in self._tools:
            if tool.name.lower() == name.lower():
                return tool
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        """Checks if the tool's run command is in the system's PATH."""
        return shutil.which(tool.run_command) is not None

    def install_tool(self, tool: Tool) -> bool:
        """Installs a tool using its defined install command."""
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
