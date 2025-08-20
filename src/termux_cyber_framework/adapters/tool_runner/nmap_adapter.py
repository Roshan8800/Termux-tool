import subprocess
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import ToolRunnerPort

class NmapAdapter(ToolRunnerPort):
    """
    A specific ToolRunnerPort implementation for the Nmap tool.
    """
    def run(self, tool: Tool, command: Command) -> Report:
        # This adapter is specific to Nmap, so it uses 'nmap' as the base command.
        # The 'tool' object is passed to conform to the port, but we could also
        # use tool.run_command if we wanted to be more dynamic.
        full_command = [tool.run_command] + command.args

        print(f"[*] Executing with Nmap-specific adapter: {' '.join(full_command)}")
        try:
            process = subprocess.run(
                full_command,
                check=False,
                capture_output=True,
                text=True,
                timeout=600 # 10-minute timeout for potentially long scans
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
            error = Error(message="Command 'nmap' not found. Is it installed and in PATH?")
            return Report(command=command, success=False, output="", error=error)
        except subprocess.TimeoutExpired as e:
            error_message = f"Nmap command timed out after {e.timeout} seconds."
            if e.stdout:
                error_message += f"\nOutput:\n{e.stdout}"
            error = Error(message=error_message)
            return Report(command=command, success=False, output=e.stdout or "", error=error)
