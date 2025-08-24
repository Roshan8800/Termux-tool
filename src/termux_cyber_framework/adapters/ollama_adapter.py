import subprocess
from typing import List, Optional
from termux_cyber_framework.core.command_runner import CommandRunner

class OllamaAdapter:
    """
    An adapter for managing the Ollama service, including starting the server
    and managing models.
    """

    def __init__(self, command_runner: CommandRunner, log_dir: str = "logs"):
        self._command_runner = command_runner
        self._log_file = f"{log_dir}/ollama.log"

    def start_server(self) -> bool:
        """
        Starts the 'ollama serve' process in the background.

        Returns:
            True if the command was sent, False otherwise.
        """
        if self.is_server_running():
            print("[+] Ollama server is already running.")
            return True

        print("[*] Starting Ollama server in the background...")
        # Using nohup and '&' to ensure the process detaches and runs in the background.
        # Output is redirected to a log file.
        command = f"nohup ollama serve > {self._log_file} 2>&1 &"
        try:
            # We use shell=True here for the backgrounding and redirection logic.
            self._command_runner.run(command, shell=True)
            print(f"[+] Ollama server started. See logs at {self._log_file}")
            # Note: This doesn't confirm the server started successfully, just that the command was issued.
            # A proper implementation might wait a few seconds and then check is_server_running().
            return True
        except Exception as e:
            print(f"[-] Failed to start Ollama server: {e}")
            return False

    def is_server_running(self) -> bool:
        """
        Checks if the 'ollama serve' process is currently running.
        """
        try:
            # pgrep is a good way to check for running processes by name.
            # The '-f' flag matches against the full command line.
            self._command_runner.run(["pgrep", "-f", "ollama serve"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            # pgrep returns a non-zero exit code if no process is found
            return False

    def pull_model(self, model_name: str) -> bool:
        """
        Pulls a model from the Ollama registry.
        """
        print(f"[*] Pulling model '{model_name}'. This may take a while...")
        try:
            # This is a blocking call. A future improvement could be to stream the output
            # and show a progress bar.
            process = self._command_runner.run(
                ["ollama", "pull", model_name],
                check=True,
                capture_output=True,
                text=True
            )
            print(process.stdout)
            print(f"[+] Successfully pulled model '{model_name}'.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Failed to pull model '{model_name}'.")
            print(e.stderr)
            return False

    def list_models(self) -> List[str]:
        """
        Lists the models that have been downloaded locally.
        """
        try:
            process = self._command_runner.run(
                ["ollama", "list"],
                check=True,
                capture_output=True,
                text=True
            )
            lines = process.stdout.strip().split('\n')
            # The first line is the header, so we skip it.
            # The model name is the first part of each line, e.g., "llama3:8b..."
            return [line.split()[0] for line in lines[1:]]
        except (subprocess.CalledProcessError, IndexError):
            return []
