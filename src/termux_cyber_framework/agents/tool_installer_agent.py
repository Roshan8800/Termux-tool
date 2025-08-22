from typing import Dict
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort, LoggerPort, LogLevel

class ToolInstallerAgent:
    """
    A dedicated agent for handling the installation of tools.
    It uses a dictionary of installer strategies to handle different installation methods.
    """
    def __init__(self, installers: Dict[str, InstallerStrategyPort], logger: LoggerPort, config: Config):
        self._installers = installers
        self.logger = logger
        self.config = config

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a tool is installed using the appropriate strategy.
        """
        installer = self._installers.get(tool.install_info.method)
        if installer:
            return installer.is_installed(tool)
        self.logger.log(f"No installer found for method '{tool.install_info.method}' for tool '{tool.name}'", level=LogLevel.WARNING)
        return False

    def install_tool(self, tool: Tool) -> bool:
        """
        Installs a tool using the appropriate strategy.
        """
        installer = self._installers.get(tool.install_info.method)
        if not installer:
            self.logger.log(f"No installer found for method '{tool.install_info.method}' for tool '{tool.name}'", level=LogLevel.ERROR)
            return False
        return installer.install(tool, self.config)

    def install_if_needed(self, tool: Tool):
        """
        Checks if a tool is installed and installs it if it is not.
        Raises a RuntimeError if the installation fails.
        """
        if not self.is_installed(tool):
            self.logger.log(f"Tool '{tool.name}' is not installed. Attempting installation.")
            if not self.config.dry_run:
                if not self.install_tool(tool):
                    self.logger.log(f"Failed to install tool '{tool.name}'.", level=LogLevel.ERROR)
                    raise RuntimeError(f"Failed to install tool '{tool.name}'.")
                self.logger.log(f"Tool '{tool.name}' installed successfully.")
            else:
                self.logger.log(f"Dry run: Skipping installation of tool '{tool.name}'.", level=LogLevel.INFO)
