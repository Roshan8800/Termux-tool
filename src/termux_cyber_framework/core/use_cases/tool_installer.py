from typing import Dict, Optional, List
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import ToolInstallerPort, InstallerStrategyPort, ToolCatalogPort

class ToolInstaller(ToolInstallerPort):
    """
    The main implementation of the ToolInstallerPort.
    """
    def __init__(self, catalog: ToolCatalogPort, installers: Dict[str, InstallerStrategyPort]):
        self._catalog = catalog
        self._installers = installers
        self._tools = None

    def _get_tools(self) -> List[Tool]:
        if self._tools is None:
            self._tools = self._catalog.get_tools()
        return self._tools

    def find_tool(self, name: str) -> Optional[Tool]:
        for tool in self._get_tools():
            if tool.name.lower() == name.lower():
                return tool
        return None

    def install_tool(self, tool: Tool, config: Config) -> bool:
        method = tool.install_info.method
        installer = self._installers.get(method)

        if not installer:
            print(f"[-] No installer found for method '{method}'.")
            return False

        print(f"[*] Using '{method}' installer for tool '{tool.name}'.")
        return installer.install(tool, config)

    def check_if_installed(self, tool: Tool) -> bool:
        method = tool.install_info.method
        installer = self._installers.get(method)

        if not installer:
            print(f"[-] No installer found for method '{method}'.")
            return False

        return installer.is_installed(tool)
