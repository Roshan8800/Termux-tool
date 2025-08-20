import subprocess
import shutil
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort
from termux_cyber_framework.core.command_runner import CommandRunner

class PkgInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools using the Termux package manager.
    """
    def __init__(self, command_runner: CommandRunner):
        self._command_runner = command_runner

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a pkg-installed tool is available.
        """
        bin_name = tool.install_info.bin_name or tool.name
        return shutil.which(bin_name) is not None

    def install(self, tool: Tool) -> bool:
        """
        Installs the tool using 'pkg install'.

        Args:
            tool: The tool to install. The `source` from `install_info` is used
                  as the package name.

        Returns:
            True if installation was successful, False otherwise.
        """
        package_name = tool.install_info.source
        command = ["pkg", "install", package_name, "-y"]

        print(f"[*] Attempting to install package '{package_name}' with pkg...")
        try:
            process = self._command_runner.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            print(process.stdout)
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"[-] Error installing package {package_name}: {e.stderr}")
            return False
        except FileNotFoundError:
            print("[-] Error: 'pkg' not found. Is Termux installed and in your PATH?")
            return False
