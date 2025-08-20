from abc import ABC, abstractmethod
from typing import Optional, List
from termux_cyber_framework.core.domain.models import Command, Tool, Report

class CommandParserPort(ABC):
    """
    A port for parsing natural language text into a structured Command.
    """
    @abstractmethod
    async def parse_command(self, text: str) -> Command:
        """
        Parses a natural language string into a structured Command object.

        Args:
            text: The user's raw input string.

        Returns:
            A Command object.
        """
        pass

class ToolManagerPort(ABC):
    """
    A port for managing cybersecurity tools.
    """
    @abstractmethod
    def find_tool(self, name: str) -> Optional[Tool]:
        """
        Finds a tool by its name from a known list or registry.

        Args:
            name: The name of the tool to find.

        Returns:
            A Tool object if found, otherwise None.
        """
        pass

    @abstractmethod
    def install_tool(self, tool: Tool) -> bool:
        """
        Installs the given tool.

        Args:
            tool: The Tool object to install.

        Returns:
            True if installation was successful, otherwise False.
        """
        pass

    @abstractmethod
    def check_if_installed(self, tool: Tool) -> bool:
        """
        Checks if a tool is already installed on the system.

        Args:
            tool: The tool to check.

        Returns:
            True if the tool is installed, otherwise False.
        """
        pass


class ToolRunnerPort(ABC):
    """
    A port for executing commands in the underlying shell.
    """
    @abstractmethod
    def run_command(self, tool: Tool, command: Command) -> Report:
        """
        Executes a command for a given tool.

        Args:
            tool: The tool that provides the base execution command.
            command: The specific command to execute, including arguments.

        Returns:
            A Report object containing the execution results.
        """
        pass
