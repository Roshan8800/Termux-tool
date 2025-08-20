import subprocess
import os
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import InstallerStrategyPort

class GitInstallerAdapter(InstallerStrategyPort):
    """
    An installer strategy for installing tools from a Git repository.
    """
    def install(self, tool: Tool) -> bool:
        """
        Installs the tool by cloning a Git repository.

        Args:
            tool: The tool to install. `install_info.source` is the git URL,
                  and `install_info.path` is the destination directory.

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
            process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            print(process.stdout)
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"[-] Error cloning repository {repo_url}: {e.stderr}")
            return False
        except FileNotFoundError:
            print("[-] Error: 'git' command not found. Is git installed?")
            return False
