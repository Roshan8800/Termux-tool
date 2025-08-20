from pydantic import BaseModel, Field
from typing import List, Optional

class Tool(BaseModel):
    """
    Represents a cybersecurity tool that can be managed and executed.
    """
    name: str = Field(..., description="The unique name of the tool (e.g., 'nmap').")
    description: str = Field(..., description="A brief description of the tool.")
    install_command: str = Field(..., description="The shell command to install the tool.")
    run_command: str = Field(..., description="The base command to execute the tool (e.g., 'nmap').")
    is_installed: bool = Field(False, description="Whether the tool is currently installed.")
    adapter_class: Optional[str] = Field(None, description="The full import path to the tool's specific adapter class.")

class Command(BaseModel):
    """
    Represents a parsed command from the user's natural language input.
    """
    tool_name: str = Field(..., description="The name of the tool to be executed.")
    args: List[str] = Field(default_factory=list, description="The arguments to pass to the tool's command.")
    raw_command: str = Field(..., description="The original natural language command from the user.")

class Error(BaseModel):
    """
    Represents an error that occurred during command execution.
    """
    error_code: Optional[int] = Field(None, description="The exit code of the failed command.")
    message: str = Field(..., description="The error message or stderr output.")
    fix_suggestion: Optional[str] = Field(None, description="A potential fix or suggestion for the error.")

class Report(BaseModel):
    """
    Represents the result of a command execution.
    """
    command: Command = Field(..., description="The command that was executed.")
    success: bool = Field(..., description="Whether the command executed successfully.")
    output: str = Field(..., description="The stdout from the command execution.")
    error: Optional[Error] = Field(None, description="Details of the error if the command failed.")
