import subprocess
import shutil
import os
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

class PkgInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools using a system package manager (apt-get or pkg).
    """
    def __init__(self, command_runner: CommandRunner, install_logger: InstallLogger):
        self._command_runner = command_runner
        self._install_logger = install_logger
        self.pkg_manager = self._get_package_manager()

    def _get_package_manager(self) -> str:
        """Determines the available package manager."""
        if shutil.which("apt-get"):
            return "apt-get"
        if shutil.which("pkg"):
            return "pkg"
        return None

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a pkg-installed tool is available.
        """
        bin_name = tool.install_info.bin_name or tool.name
        return shutil.which(bin_name) is not None

    def install(self, tool: Tool, config: Config) -> bool:
        """
        Installs the tool using the detected package manager.
        """
        if not self.pkg_manager:
            message = "No supported package manager (apt-get, pkg) found."
            self._install_logger.log(tool.name, message)
            print(f"[-] {message}")
            return False

        if not config.allow_system_install:
            if os.geteuid() == 0:
                message = "Running as root is not allowed by policy."
                self._install_logger.log(tool.name, message)
                raise PermissionError(message)
            message = f"System-level installation for '{tool.name}' is not allowed by policy."
            self._install_logger.log(tool.name, message)
            raise PermissionError(message)

        package_name = tool.install_info.source

        use_sudo = self.pkg_manager == "apt-get" and os.geteuid() != 0 and shutil.which("sudo")

        command = [self.pkg_manager, "install", package_name, "-y"]
        if use_sudo:
            command.insert(0, "sudo")

        print(f"[*] Attempting to install package '{package_name}' with {self.pkg_manager}...")
        try:
            # For apt-get, we might need to run `apt-get update` first.
            if self.pkg_manager == "apt-get":
                update_command = ["apt-get", "update"]
                if use_sudo:
                    update_command.insert(0, "sudo")
                print(f"[*] Running '{' '.join(update_command)}'...")
                self._command_runner.run(update_command, check=True, capture_output=True, text=True)

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
            print(f"[-] Error installing package {package_name}: {e.stderr}")
            return False
        except FileNotFoundError:
            self._install_logger.log(tool.name, f"Error: '{self.pkg_manager}' not found.")
            print(f"[-] Error: '{self.pkg_manager}' not found. Is it installed and in your PATH?")
            return False
