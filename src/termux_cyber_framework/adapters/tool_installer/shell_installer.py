import subprocess
import shutil
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

class ShellInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools by executing a shell script.
    """
    def __init__(self, command_runner: CommandRunner, install_logger: InstallLogger):
        self._command_runner = command_runner
        self._install_logger = install_logger

    def is_installed(self, tool: Tool) -> bool:
        """
        Checks if a shell-script-installed tool is available by checking for its binary.
        """
        bin_name = tool.install_info.bin_name or tool.name
        return shutil.which(bin_name) is not None

    def install(self, tool: Tool, config: Config) -> bool:
        """
        Installs the tool by executing the shell command provided in the tool's source.
        """
        install_command = tool.install_info.source
        print(f"[*] Attempting to install '{tool.name}' by executing shell command...")
        self._install_logger.log(tool.name, f"Executing: {install_command}")

        try:
            # We need to run this with shell=True because of pipes and redirects.
            # This is a controlled use case where the command comes from our trusted catalog.
            process = self._command_runner.run(
                install_command,
                shell=True, # Required for commands like `curl ... | sh`
                check=True,
                capture_output=True,
                text=True
            )
            self._install_logger.log(tool.name, process.stdout)
            self._install_logger.log(tool.name, process.stderr)
            print(f"[+] '{tool.name}' installation script executed successfully.")
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            self._install_logger.log(tool.name, e.stdout)
            self._install_logger.log(tool.name, e.stderr)
            print(f"[-] Error installing {tool.name}: {e.stderr}")
            return False
        except Exception as e:
            error_message = f"An unexpected error occurred during the installation of {tool.name}: {e}"
            self._install_logger.log(tool.name, error_message)
            print(f"[-] {error_message}")
            return False
