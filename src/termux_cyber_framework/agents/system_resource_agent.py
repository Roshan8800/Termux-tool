import re
import subprocess
from typing import Optional

from termux_cyber_framework.core.command_runner import CommandRunner

class SystemResourceAgent:
    """
    An agent responsible for checking and reporting system resources
    like storage, memory, and CPU.
    """

    def __init__(self, command_runner: CommandRunner):
        self._command_runner = command_runner

    def get_available_storage_mb(self, path: str = ".") -> Optional[int]:
        """
        Checks the available disk space for a given path.

        Args:
            path: The file system path to check. Defaults to the current directory.

        Returns:
            The available space in megabytes (MB), or None if it cannot be determined.
        """
        command = ["df", "-k", path]
        try:
            process = self._command_runner.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            output = process.stdout

            # The output looks like:
            # Filesystem     1K-blocks     Used Available Use% Mounted on
            # /dev/root      ...           ...  28734320  ...  /
            lines = output.strip().split('\n')
            if len(lines) < 2:
                return None

            # The second line contains the data
            parts = re.split(r'\s+', lines[1])
            if len(parts) < 4:
                return None

            # The 'Available' space is the 4th column (index 3)
            available_kb = int(parts[3])
            return available_kb // 1024

        except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError) as e:
            # Log this error in a real scenario
            print(f"Error checking storage: {e}")
            return None
