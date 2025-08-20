import subprocess
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import ToolRunnerPort

class ShellToolRunnerAdapter(ToolRunnerPort):
    """
    An adapter that runs tool commands in the local shell.
    """
    def run_command(self, tool: Tool, command: Command) -> Report:
        full_command = [tool.run_command] + command.args
        print(f"[*] Executing: {' '.join(full_command)}")
        try:
            process = subprocess.run(
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
