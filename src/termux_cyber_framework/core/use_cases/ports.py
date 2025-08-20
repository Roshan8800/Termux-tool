from abc import ABC, abstractmethod
from typing import Optional, List
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, Error
from termux_cyber_framework.core.domain.config import Config
from enum import Enum


class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class LoggerPort(ABC):
    """
    A port for logging framework activity.
    """
    @abstractmethod
    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        pass


class CommandParserPort(ABC):
    """
    A port for parsing natural language text into a structured Command.
    """
    @abstractmethod
    async def parse_command(self, text: str) -> Command:
        pass


class InstallerStrategyPort(ABC):
    """
    A port for a specific installation strategy (e.g., git, pip).
    """
    @abstractmethod
    def install(self, tool: Tool, config: Config) -> bool:
        """
        Installs the given tool using the specific strategy.

        Args:
            tool: The tool to install.
            config: The framework configuration.

        Returns:
            True if installation was successful, False otherwise.
        """
        pass


class ToolInstallerPort(ABC):
    """
    A port for managing the installation of cybersecurity tools.
    """
    @abstractmethod
    def find_tool(self, name: str) -> Optional[Tool]:
        pass

    @abstractmethod
    def install_tool(self, tool: Tool, config: Config) -> bool:
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
    def run(self, tool: Tool, command: Command) -> ExecutionResult:
        """
        Runs the given command for the given tool.

        Args:
            tool: The tool definition, containing the base run command.
            command: The command object containing args.

        Returns:
            A ExecutionResult object with the execution results.
        """
        pass

class ReportGeneratorPort(ABC):
    """
    A port for generating and outputting a report.
    """
    @abstractmethod
    def generate(self, result: ExecutionResult) -> None:
        """
        Generates and outputs the given report.

        Args:
            result: The execution result to be generated.
        """
        pass


class ErrorFixerPort(ABC):
    """
    A port for an AI-driven component that suggests fixes for failed commands.
    """
    @abstractmethod
    async def suggest_fix(self, error: Error, command: Command) -> Optional[Command]:
        """
        Analyzes an error and suggests a new, corrected command.

        Args:
            error: The error that occurred.
            command: The original command that failed.

        Returns:
            A new Command object with a suggested fix, or None if no fix
            can be determined.
        """
        pass


class DoctorPort(ABC):
    """
    A port for detecting and fixing common issues.
    """
    @abstractmethod
    def detect_and_fix(self, result: ExecutionResult) -> List[dict]:
        """
        Inspects the result of a command execution and applies fixes.
        """
        pass
