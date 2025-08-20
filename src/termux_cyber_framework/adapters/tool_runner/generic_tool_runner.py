import subprocess
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import ToolRunnerPort
from termux_cyber_framework.core.command_runner import CommandRunner

class GenericToolRunnerAdapter(ToolRunnerPort):
    """
    A generic adapter that runs any tool command in the local shell.
    This serves as a fallback for tools without a specific adapter.
    """
    def __init__(self, command_runner: CommandRunner = None):
        self._command_runner = command_runner or CommandRunner()

    def run(self, tool: Tool, command: Command) -> Report:
        # Split the base command from the tool definition and combine with user args
        base_command_parts = tool.run_command.split()
        full_command = base_command_parts + command.args

        print(f"[*] Executing with generic fallback runner: {' '.join(full_command)}")
        try:
            process = self._command_runner.run(
                full_command,
                check=False,  # We handle the error manually
                capture_output=True,
                text=True,
                timeout=300 # 5-minute timeout
            )

            if process.returncode == 0:
                return Report(
                    command=command,
                    success=True,
                    output=process.stdout,
                    error=None
                )
            else:
                error = Error(
                    error_code=process.returncode,
                    message=process.stderr or process.stdout
                )
                return Report(command=command, success=False, output=process.stdout, error=error)

        except FileNotFoundError:
            error = Error(message=f"Command not found: {tool.run_command}. Is it installed and in PATH?")
            return Report(command=command, success=False, output="", error=error)
        except subprocess.TimeoutExpired as e:
            error_message = f"Command timed out after {e.timeout} seconds."
            if e.stdout:
                error_message += f"\nOutput:\n{e.stdout}"
            error = Error(message=error_message)
            return Report(command=command, success=False, output=e.stdout or "", error=error)
