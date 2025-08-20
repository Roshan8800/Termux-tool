from abc import ABC, abstractmethod
from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Tool, Report

class CommandParserPort(ABC):
    """
    A port for parsing natural language text into a structured Command.
    """
    @abstractmethod
    async def parse_command(self, text: str) -> Command:
        pass

class ToolInstallerPort(ABC):
    """
    A port for managing the installation of cybersecurity tools.
    """
    @abstractmethod
    def find_tool(self, name: str) -> Optional[Tool]:
        pass

    @abstractmethod
    def install_tool(self, tool: Tool) -> bool:
        pass

    @abstractmethod
    def check_if_installed(self, tool: Tool) -> bool:
        pass

class ToolRunnerPort(ABC):
    """
    A port for executing a command for a specific tool.
    Each tool adapter will implement this port.
    """
    @abstractmethod
    def run(self, tool: Tool, command: Command) -> Report:
        """
        Runs the given command for the given tool.

        Args:
            tool: The tool definition, containing the base run command.
            command: The command object containing args.

        Returns:
            A Report object with the execution results.
        """
        pass

class ReportGeneratorPort(ABC):
    """
    A port for generating and outputting a report.
    """
    @abstractmethod
    def generate(self, report: Report) -> None:
        """
        Generates and outputs the given report.

        Args:
            report: The report to be generated.
        """
        pass
