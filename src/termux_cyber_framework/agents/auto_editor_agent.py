import subprocess
from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Error
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from .file_manager_agent import FileManagerAgent

class AutoEditorAgent:
    """
    An agent that uses the Central AI Service to automatically patch scripts
    that have caused errors.
    """
    def __init__(self, ai_service: AIProcessingPort, file_manager: FileManagerAgent):
        self.ai_service = ai_service
        self.file_manager = file_manager

    async def patch_script(self, script_path: str, error: Error, command: Command) -> bool:
        """
        Attempts to automatically patch a script file based on an execution error.

        Args:
            script_path: The path to the script file to patch.
            error: The error that occurred during execution.
            command: The command that was run.

        Returns:
            True if the patch was successfully generated and applied, False otherwise.
        """
        script_content = self.file_manager.read_file(script_path)
        if not script_content:
            return False

        try:
            patch = await self.ai_service.generate_script_patch(script_content, error, command)
            if not patch:
                return False

            # Apply the patch using the `patch` command-line utility
            process = subprocess.run(
                ['patch', script_path],
                input=patch,
                text=True,
                capture_output=True,
                check=True
            )
            return process.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, Exception):
            return False
