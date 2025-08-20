import subprocess
import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, Error
from termux_cyber_framework.core.use_cases.ports import ToolRunnerPort
from termux_cyber_framework.core.command_runner import CommandRunner

class GenericRunner(ToolRunnerPort):
    """
    A generic adapter that runs any tool command in the local shell.
    This serves as a fallback for tools without a specific adapter.
    """
    def __init__(self, command_runner: CommandRunner = None, reports_dir="reports"):
        self._command_runner = command_runner or CommandRunner()
        self.reports_dir = reports_dir

    def run(self, tool: Tool, command: Command) -> ExecutionResult:
        base_command_parts = tool.run_command.split()
        full_command = base_command_parts + command.args

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        output_log_dir = os.path.join(self.reports_dir, date_str, tool.name)
        if not os.path.exists(output_log_dir):
            os.makedirs(output_log_dir)
        output_log_file = os.path.join(output_log_dir, f"{time_str}.log")

        start_time = datetime.now()

        try:
            process = self._command_runner.run(
                full_command,
                timeout=300, # 5-minute timeout
                output_log_file=output_log_file
            )

            end_time = datetime.now()

            if process.returncode == 0:
                return ExecutionResult(
                    command=command,
                    success=True,
                    output=process.stdout,
                    error=None,
                    start_time=start_time,
                    end_time=end_time,
                    pid=process.pid,
                    output_log_file=output_log_file
                )
            else:
                error = Error(
                    error_code=process.returncode,
                    message=process.stderr or process.stdout
                )
                return ExecutionResult(
                    command=command,
                    success=False,
                    output=process.stdout,
                    error=error,
                    start_time=start_time,
                    end_time=end_time,
                    pid=process.pid,
                    output_log_file=output_log_file
                )

        except FileNotFoundError:
            end_time = datetime.now()
            error = Error(message=f"Command not found: {tool.run_command}. Is it installed and in PATH?")
            return ExecutionResult(
                command=command,
                success=False,
                output="",
                error=error,
                start_time=start_time,
                end_time=end_time,
                output_log_file=output_log_file
            )
        except subprocess.TimeoutExpired as e:
            end_time = datetime.now()
            error_message = f"Command timed out after {e.timeout} seconds."
            if e.stdout:
                error_message += f"\nOutput:\n{e.stdout}"
            error = Error(message=error_message)
            return ExecutionResult(
                command=command,
                success=False,
                output=e.stdout or "",
                error=error,
                start_time=start_time,
                end_time=end_time,
                output_log_file=output_log_file
            )
