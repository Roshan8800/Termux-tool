import subprocess
import os
import sys
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

class GitInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools from a Git repository.
    """
    def __init__(self, command_runner: CommandRunner, install_logger: InstallLogger):
        self._command_runner = command_runner
        self._install_logger = install_logger

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a git-installed tool is present and healthy.
        """
        path = tool.install_info.path
        if not path or not os.path.exists(path):
            return False

        health_check = tool.install_info.health_check
        if not health_check:
            return True
        try:
            # Using shell=True for complex commands, be cautious
            self._command_runner.run(
                health_check,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def install(self, tool: Tool, config: Config) -> bool:
        """
        Installs the tool by cloning a Git repository.

        Args:
            tool: The tool to install. `install_info.source` is the git URL,
                  and `install_info.path` is the destination directory.
            config: The framework configuration (unused).

        Returns:
            True if cloning was successful, False otherwise.
        """
        repo_url = tool.install_info.source
        clone_path = tool.install_info.path

        if not clone_path:
            print(f"[-] Error: No destination path specified for git clone for tool '{tool.name}'.")
            return False

        # Ensure the parent directory for the clone path exists
        parent_dir = os.path.dirname(clone_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        command = ["git", "clone", repo_url, clone_path]

        print(f"[*] Attempting to clone git repository '{repo_url}' into '{clone_path}'...")
        try:
            process = self._command_runner.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            self._install_logger.log(tool.name, process.stdout)
            self._install_logger.log(tool.name, process.stderr)

            # After successful clone, check for requirements.txt
            requirements_path = os.path.join(clone_path, "requirements.txt")
            if os.path.exists(requirements_path):
                print(f"[*] Found requirements.txt. Installing Python dependencies for '{tool.name}'...")
                self._install_logger.log(tool.name, "Found requirements.txt, installing dependencies.")

                pip_command = [sys.executable, "-m", "pip", "install", "-r", requirements_path]
                try:
                    pip_process = self._command_runner.run(
                        pip_command,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    self._install_logger.log(tool.name, "Pip dependencies installed successfully.")
                    self._install_logger.log(tool.name, pip_process.stdout)
                except subprocess.CalledProcessError as pip_e:
                    error_msg = f"Failed to install pip dependencies for '{tool.name}'."
                    self._install_logger.log(tool.name, error_msg)
                    self._install_logger.log(tool.name, pip_e.stderr)
                    print(f"[-] {error_msg}")
                    return False

            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            self._install_logger.log(tool.name, e.stdout)
            self._install_logger.log(tool.name, e.stderr)
            print(f"[-] Error cloning repository {repo_url}: {e.stderr}")
            return False
        except FileNotFoundError:
            self._install_logger.log(tool.name, "Error: 'git' command not found.")
            print("[-] Error: 'git' command not found. Is git installed?")
            return False
