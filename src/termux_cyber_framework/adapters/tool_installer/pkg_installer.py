import subprocess
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort

class PkgInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools using a system package manager.
    This adapter uses 'apt-get' for compatibility with Debian-based systems.
    """
    def install(self, tool: Tool) -> bool:
        """
        Installs the tool using 'sudo apt-get install'.

        Args:
            tool: The tool to install. The `source` from `install_info` is used
                  as the package name.

        Returns:
            True if installation was successful, False otherwise.
        """
        package_name = tool.install_info.source
        command = ["sudo", "apt-get", "install", package_name, "-y"]

        print(f"[*] Attempting to install package '{package_name}' with apt-get...")
        try:
            process = subprocess.run(
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
            print("[-] Error: 'sudo' or 'apt-get' not found. Is this a Debian-based system?")
            return False
