import shutil
from typing import Optional
from termux_cyber_framework.core.domain.models import Tool, ExecutionResult, Command
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort, LoggerPort, InstallerStrategyPort, LogLevel
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.adapters.tool_runner.generic_runner import GenericRunner
from typing import Dict

class GenericToolAdapter(ToolAdapterPort):
    """
    A generic adapter for tools that don't have a specific implementation.
    It uses the GenericRunner to execute commands and delegates installation.
    """
    def __init__(self, tool: Tool, command_runner: CommandRunner, logger: LoggerPort, config: Config, installers: Dict[str, InstallerStrategyPort]):
        self._tool = tool
        self._runner = GenericRunner(command_runner)
        self.config = config
        self.logger = logger
        self._installers = installers

    def find_tool(self, name: str) -> Optional[Tool]:
        if name.lower() == self._tool.name.lower():
            return self._tool
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        installer = self._installers.get(tool.install_info.method)
        if installer:
            return installer.is_installed(tool)
        return shutil.which(tool.run_command) is not None

    def install_tool(self, tool: Tool) -> bool:
        installer = self._installers.get(tool.install_info.method)
        if not installer:
            self.logger.log(f"No installer found for method '{tool.install_info.method}' for tool '{tool.name}'", level=LoggerPort.LogLevel.ERROR)
            return False
        return installer.install(tool, self.config)

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        return self._runner.run(tool, command, paths)
