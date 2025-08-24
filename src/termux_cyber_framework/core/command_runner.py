import subprocess
import os
import signal
import time
from typing import List, Optional

class CommandRunner:
    """
    A wrapper around subprocess.run to make it easier to mock in tests,
    with soft/hard kill mechanism and output logging.
    """
    def run(self, command: List[str], timeout: int = 300, output_log_file: Optional[str] = None, interactive: bool = False, **kwargs):
        """
        Runs a command using subprocess.Popen to have more control over the process.

        Args:
            command: The command to run.
            timeout: The timeout in seconds.
            output_log_file: The file to log stdout and stderr to.
            interactive: If True, run in interactive mode, inheriting stdio.
            **kwargs: Additional arguments to pass to Popen.
        """
        if interactive:
            # For interactive processes, we don't capture streams.
            # They are inherited from the parent.
            try:
                process = subprocess.Popen(command, **kwargs)
                process.wait(timeout=timeout)
                return subprocess.CompletedProcess(process.args, process.returncode, None, None)
            except subprocess.TimeoutExpired:
                process.send_signal(signal.SIGTERM)
                raise
            except Exception:
                # In case of other errors, we still want to return a consistent object
                return subprocess.CompletedProcess(command, 1, None, "Failed to run interactive command.")

        # Non-interactive, logging-focused execution
        start_time = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)

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
                process.communicate(timeout=10) # 10 seconds for graceful shutdown
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            if output_log_file:
                 with open(output_log_file, "a") as log_file:
                    log_file.write("\n--- TIMEOUT ---\n")
            raise
