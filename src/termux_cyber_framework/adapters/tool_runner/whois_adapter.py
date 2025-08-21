import shutil
import subprocess
from .generic_runner import GenericRunner
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort, LoggerPort

class WhoisAdapter(GenericRunner, ToolAdapterPort):
    """
    A specific ToolAdapterPort implementation for the whois tool.
    """
    def __init__(self, command_runner: CommandRunner = None, config: Config = None, logger: LoggerPort = None):
        super().__init__(command_runner)
        self.config = config or Config()
        self.logger = logger

    def find_tool(self, name: str):
        if name == "whois":
            return Tool(
                name="whois",
                description="Whois client",
                install_info=InstallInfo(method="pkg", source="whois"),
                run_command="whois"
            )
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        return shutil.which("whois") is not None

    def install_tool(self, tool: Tool) -> bool:
        if not self.config.allow_system_install:
            print(f"[-] System-level installation for '{tool.name}' is not allowed by policy.")
            return False

        try:
            process = self._command_runner.run(["pkg", "install", "whois", "-y"])
            if self.logger:
                log_file = f"logs/install-{tool.name}.log"
                with open(log_file, "w") as f:
                    f.write(process.stdout)
                    f.write(process.stderr)
            return process.returncode == 0
        except Exception as e:
            if self.logger:
                log_file = f"logs/install-{tool.name}-error.log"
                with open(log_file, "w") as f:
                    f.write(str(e))
            return False
