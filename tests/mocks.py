import subprocess
from typing import List, Optional

class MockCommandRunner:
    """
    A mock command runner that can be used in tests.
    """
    def __init__(self, mock_results: Optional[dict] = None):
        self.mock_results = mock_results or {}

    def run(self, command: List[str], **kwargs):
        """
        Mocks the run method.
        """
        if isinstance(command, list):
            command_str = " ".join(command)
        else:
            command_str = command

        if command_str in self.mock_results:
            result = self.mock_results[command_str]
            if "exception" in result:
                raise result["exception"]
            return subprocess.CompletedProcess(
                args=command,
                returncode=result.get("returncode", 0),
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
            )
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )
