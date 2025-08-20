import subprocess
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort

class PipInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing Python packages using pip.
    """
    def install(self, tool: Tool) -> bool:
        """
        Installs a Python package using 'pip'.

        Args:
            tool: The tool to install. `install_info.source` is used as the
                  pip package name.

        Returns:
            True if installation was successful, False otherwise.
        """
        package_name = tool.install_info.source
        # Using 'python3 -m pip' is generally more reliable than 'pip' directly
        command = ["python3", "-m", "pip", "install", package_name]

        print(f"[*] Attempting to install pip package '{package_name}'...")
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
            print(f"[-] Error installing pip package {package_name}: {e.stderr}")
            return False
        except FileNotFoundError:
            print("[-] Error: 'python3' or 'pip' not found. Is Python 3 with pip installed?")
            return False
