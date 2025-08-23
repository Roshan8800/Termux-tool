from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .run_paths import RunPaths

class InstallInfo(BaseModel):
    """
    Defines the installation method and source for a tool.
    """
    method: str = Field(..., description="The installation method, e.g., 'git', 'pip', 'pkg'.")
    source: str = Field(..., description="The source for the installation, e.g., a URL or package name.")
    path: Optional[str] = Field(None, description="The destination path for installation, e.g., for git clones.")
    health_check: Optional[str] = Field(None, description="A command to run to check if the tool is functional.")
    python_module: Optional[str] = Field(None, description="The Python module to import for checking installation.")
    bin_name: Optional[str] = Field(None, description="The binary name of the tool if it differs from the tool name.")


class Tool(BaseModel):
    """
    Represents a cybersecurity tool that can be managed and executed.
    """
    name: str = Field(..., description="The unique name of the tool (e.g., 'nmap').")
    description: str = Field(..., description="A brief description of the tool.")
    install_info: InstallInfo = Field(..., description="Details for how to install the tool.")
    run_command: Optional[str] = Field(None, description="The base command to execute the tool (e.g., 'nmap').")
    is_installed: bool = Field(False, description="Whether the tool is currently installed.")
    adapter_class: Optional[str] = Field(None, description="The full import path to the tool's specific adapter class.")

class Command(BaseModel):
    """
    Represents a parsed command from the user's natural language input.
    """
    tool_name: str = Field(..., description="The name of the tool to be executed.")
    args: List[str] = Field(default_factory=list, description="The arguments to pass to the tool's command.")
    raw_command: str = Field(..., description="The original natural language command from the user.")
    ai_interpretation: Optional[dict] = Field(None, description="The structured interpretation from the AI.")

class Error(BaseModel):
    """
    Represents an error that occurred during command execution.
    """
    error_code: Optional[int] = Field(None, description="The exit code of the failed command.")
    message: str = Field(..., description="The error message or stderr output.")
    fix_suggestion: Optional[str] = Field(None, description="A potential fix or suggestion for the error.")
    ai_analysis: Optional[str] = Field(None, description="An AI-generated analysis of the error.")

class ExecutionResult(BaseModel):
    """
    Represents the result of a command execution.
    """
    command: Command = Field(..., description="The command that was executed.")
    success: bool = Field(..., description="Whether the command executed successfully.")
    output: str = Field(..., description="The stdout from the command execution.")
    error: Optional[Error] = Field(None, description="Details of the error if the command failed.")
    start_time: datetime = Field(..., description="The timestamp when the command started.")
    end_time: datetime = Field(..., description="The timestamp when the command ended.")
    pid: Optional[int] = Field(None, description="The process ID of the command.")
    paths: Optional[RunPaths] = Field(None, description="The paths used for report and log files.")
    output_log_file: Optional[str] = Field(None, description="The path to the log file containing the command's output.")
    findings: Optional[List[dict]] = Field(None, description="A list of structured findings from the tool's output.")
    consent_given: bool = Field(False, description="Whether the user provided consent for the command to be executed.")
    ai_advice: Optional[str] = Field(None, description="An AI-generated suggestion for the next action.")


class Remediation(BaseModel):
    """
    Represents a suggested remediation for an error.
    """
    description: str = Field(..., description="A description of the suggested fix.")
    command: Command = Field(..., description="The corrected command to run.")
