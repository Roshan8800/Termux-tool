import shutil
from typing import Optional
from termux_cyber_framework.core.domain.models import Tool, ExecutionResult, Command
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort, LoggerPort
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.adapters.tool_runner.generic_runner import GenericRunner

class GenericToolAdapter(ToolAdapterPort):
    """
    A generic adapter for tools that don't have a specific implementation.
    It uses the GenericRunner to execute commands.
    """
    def __init__(self, tool: Tool, command_runner: CommandRunner, logger: LoggerPort, config: Config):
        self._tool = tool
        self._runner = GenericRunner(command_runner)
        self.config = config
        self.logger = logger

    def find_tool(self, name: str) -> Optional[Tool]:
        if name.lower() == self._tool.name.lower():
            return self._tool
        return None

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        return self._runner.run(tool, command, paths)
