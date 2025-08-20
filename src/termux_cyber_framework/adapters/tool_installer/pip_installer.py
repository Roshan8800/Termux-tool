import subprocess
import shutil
import os
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

class PipInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing Python packages using pip.
    """
    def __init__(self, command_runner: CommandRunner, install_logger: InstallLogger):
        self._command_runner = command_runner
        self._install_logger = install_logger

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a pip-installed tool is available.
        """
        module_name = tool.install_info.python_module
        if module_name:
            try:
                self._command_runner.run(
                    ["python3", "-c", f"import {module_name}"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False

        bin_name = tool.install_info.bin_name or tool.name
        return shutil.which(bin_name) is not None

    def install(self, tool: Tool, config: Config) -> bool:
        """
        Installs a Python package using 'pip'.

        Args:
            tool: The tool to install. `install_info.source` is used as the
                  pip package name.
            config: The framework configuration.

        Returns:
            True if installation was successful, False otherwise.
        """
        if not config.allow_system_install:
            if os.geteuid() == 0:
                message = "Running as root is not allowed by policy."
                self._install_logger.log(tool.name, message)
                raise PermissionError(message)
            message = f"System-level installation for '{tool.name}' is not allowed by policy."
            self._install_logger.log(tool.name, message)
            raise PermissionError(message)

        package_name = tool.install_info.source
        # Using 'python3 -m pip' is generally more reliable than 'pip' directly
        command = ["python3", "-m", "pip", "install", package_name]

        print(f"[*] Attempting to install pip package '{package_name}'...")
        try:
            process = self._command_runner.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            self._install_logger.log(tool.name, process.stdout)
            self._install_logger.log(tool.name, process.stderr)
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            self._install_logger.log(tool.name, e.stdout)
            self._install_logger.log(tool.name, e.stderr)
            print(f"[-] Error installing pip package {package_name}: {e.stderr}")
            return False
        except FileNotFoundError:
            self._install_logger.log(tool.name, "Error: 'python3' or 'pip' not found.")
            print("[-] Error: 'python3' or 'pip' not found. Is Python 3 with pip installed?")
            return False
