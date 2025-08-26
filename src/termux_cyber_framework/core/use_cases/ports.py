from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from termux_cyber_framework.core.domain.models import (
    Command, Tool, ExecutionResult, Error, Remediation)
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
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
    def install(self, tool: Tool) -> bool:
        """
        Installs the given tool using the specific strategy.

        Args:
            tool: The tool to install.

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
    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        """
        Runs the given command for the given tool.

        Args:
            tool: The tool definition, containing the base run command.
            command: The command object containing args.
            paths: The paths for the report files.

        Returns:
            A ExecutionResult object with the execution results.
        """
        pass

class ToolAdapterPort(ToolRunnerPort):
    """
    A port for a tool adapter that handles execution.
    Installation is now handled by the ToolInstallerAgent.
    """
    @abstractmethod
    def find_tool(self, name: str) -> Optional[Tool]:
        """
        Finds the tool definition this adapter is responsible for.
        """
        pass

class ReportGeneratorPort(ABC):
    """
    A port for generating and outputting a report.
    """
    @abstractmethod
    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        """
        Prepares the paths for the report files.

        Returns:
            A RunPaths object with the summary and run log paths.
        """
        pass

    @abstractmethod
    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Generates and outputs the given report.

        Args:
            result: The execution result to be generated.
        """
        pass

class AuditLoggerPort(ABC):
    """
    A port for logging audit events.
    """
    @abstractmethod
    def append(self, event: dict) -> None:
        """
        Appends an event to the audit log.
        """
        pass

class ToolCatalogPort(ABC):
    """
    A port for getting available tools.
    """
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """
        Returns a list of available tools.
        """
        pass

class ConsentPort(ABC):
    """
    A port for getting user consent.
    """
    @abstractmethod
    def get_consent(self, command: Command) -> bool:
        """
        Gets consent from the user to run a command.
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
    A port for diagnosing and suggesting remediations for errors.
    """
    @abstractmethod
    def diagnose(self, error: Error, command: Command) -> list[Remediation]:
        """
        Diagnoses an error and returns a list of possible remediations.
        """
        pass

class NetworkPort(ABC):
    """
    A port for checking network connectivity.
    """
    @abstractmethod
    def check_internet_connection(self) -> bool:
        """
        Checks for an active internet connection.
        """
        pass


class AIProcessingPort(ABC):
    """
    A unified port for all AI model interactions, acting as the interface
    for the 'Central AI Brain'.
    """
    @abstractmethod
    async def interpret_master_command(self, user_input: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def interpret_tool_command(self, user_input: str, tool_catalog: List[Dict[str, Any]]) -> Command:
        pass

    @abstractmethod
    async def plan_scenario(self, goal: str) -> List[Command]:
        pass

    @abstractmethod
    async def analyze_error(self, command: Command, error: Error) -> str:
        pass

    @abstractmethod
    async def suggest_command_fix(self, command: Command, error: Error) -> Optional[Command]:
        pass

    @abstractmethod
    async def generate_script_patch(self, script_content: str, error: Error, command: Command) -> str:
        pass

    @abstractmethod
    async def answer_knowledge_question(self, question: str, tool_context: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def extract_data_from_output(self, result: ExecutionResult) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def summarize_execution_result(self, result: ExecutionResult) -> str:
        pass
