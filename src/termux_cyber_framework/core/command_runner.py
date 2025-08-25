import subprocess
import os
import signal
import time
from typing import List, Optional

class CommandRunner:
    """
    A wrapper around subprocess to make it easier to mock in tests.
    It can run commands interactively, as a blocking call, or as a managed process.
    """
    def run(
        self,
        command: List[str],
        timeout: int = 300,
        output_log_file: Optional[str] = None,
        interactive: bool = False,
        just_get_process: bool = False,
        **kwargs
    ):
        """
        Runs a command using subprocess.Popen to have more control over the process.

        Args:
            command: The command to run.
            timeout: The timeout in seconds for non-interactive commands.
            output_log_file: The file to log stdout and stderr to for non-interactive commands.
            interactive: If True, run in interactive mode, inheriting stdio.
            just_get_process: If True, returns the Popen object immediately for background process management.
            **kwargs: Additional arguments to pass to Popen.
        """
        if interactive:
            # For interactive processes, we don't capture streams. They are inherited.
            try:
                process = subprocess.Popen(command, **kwargs)
                process.wait(timeout=timeout)
                return subprocess.CompletedProcess(process.args, process.returncode, None, None)
            except subprocess.TimeoutExpired:
                process.send_signal(signal.SIGTERM)
                raise
            except Exception:
                return subprocess.CompletedProcess(command, 1, None, "Failed to run interactive command.")

        # For non-interactive commands that need to be managed (e.g., background services)
        if just_get_process:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)
            return process

        # Default: Non-interactive, logging-focused execution that waits for completion
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)

        if output_log_file:
            log_dir = os.path.dirname(output_log_file)
            if not os.path.exists(log_dir) and log_dir:
                os.makedirs(log_dir)
            with open(output_log_file, "w") as log_file:
                log_file.write(f"--- Running command: {' '.join(command)} ---\n")

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            if output_log_file:
                with open(output_log_file, "a") as log_file:
                    log_file.write("\n--- STDOUT ---\n")
                    log_file.write(stdout)
                    log_file.write("\n--- STDERR ---\n")
                    log_file.write(stderr)
            return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            process.send_signal(signal.SIGTERM)
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            if output_log_file:
                 with open(output_log_file, "a") as log_file:
                    log_file.write("\n--- TIMEOUT ---\n")
            raise
