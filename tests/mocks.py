import subprocess
import os
from typing import List, Optional

class MockCommandRunner:
    """
    A mock command runner that can be used in tests.
    """
    def __init__(self, mock_results: Optional[dict] = None):
        self.mock_results = mock_results or {}
        self.call_count = 0
        self.last_command = None

    def run(self, command: List[str], **kwargs):
        self.call_count += 1
        self.last_command = command
        if isinstance(command, list):
            command_str = " ".join(command)
        else:
            command_str = command

        if command_str in self.mock_results:
            result = self.mock_results[command_str]
            if "exception" in result:
                raise result["exception"]

            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")

            if 'output_log_file' in kwargs:
                log_file = kwargs['output_log_file']
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir) and log_dir:
                    os.makedirs(log_dir)
                with open(log_file, "w") as f:
                    f.write(f"--- Running command: {command_str} ---\n")
                    f.write(f"\n--- STDOUT ---\n{stdout}")
                    f.write(f"\n--- STDERR ---\n{stderr}")

            process = subprocess.CompletedProcess(
                args=command,
                returncode=result.get("returncode", 0),
                stdout=stdout,
                stderr=stderr,
            )
            process.pid = 1234
            return process

        process = subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )
        process.pid = 1234
        return process
