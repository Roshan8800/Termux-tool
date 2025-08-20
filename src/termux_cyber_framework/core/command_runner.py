import subprocess
from typing import List

class CommandRunner:
    """
    A wrapper around subprocess.run to make it easier to mock in tests.
    """
    def run(self, command: List[str], **kwargs):
        """
        Runs a command using subprocess.run.
        """
        return subprocess.run(command, **kwargs)
