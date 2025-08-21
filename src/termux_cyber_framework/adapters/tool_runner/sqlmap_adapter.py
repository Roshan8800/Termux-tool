import re
import os
import subprocess
from .generic_runner import GenericRunner
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort, LoggerPort

class SqlmapAdapter(GenericRunner, ToolAdapterPort):
    """
    A specific ToolAdapterPort implementation for the Sqlmap tool.
    """
    def __init__(self, command_runner: CommandRunner = None, config: Config = None, logger: LoggerPort = None):
        super().__init__(command_runner)
        self.config = config or Config()
        self.logger = logger
        self.tool_path = "tools/sqlmap"

    def find_tool(self, name: str):
        if name == "sqlmap":
            return Tool(
                name="sqlmap",
                description="SQL injection tool",
                install_info=InstallInfo(method="git", source="https://github.com/sqlmapproject/sqlmap.git", path=self.tool_path),
                run_command=f"python3 {self.tool_path}/sqlmap.py"
            )
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        return os.path.exists(self.tool_path)

    def install_tool(self, tool: Tool) -> bool:
        if not self.config.allow_system_install:
            print(f"[-] System-level installation for '{tool.name}' is not allowed by policy.")
            return False

        try:
            process = self._command_runner.run(["git", "clone", "https://github.com/sqlmapproject/sqlmap.git", self.tool_path])
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

    def _parse_output(self, output: str) -> list:
        findings = []
        # Example parsing logic, can be expanded
        for line in output.splitlines():
            if "parameter" in line and "vulnerable" in line:
                match = re.search(r"parameter '(.+?)' is vulnerable\..+?the back-end DBMS is (.+)", line)
                if not match:
                    match = re.search(r"parameter '(.+?)' is vulnerable. a (.+?) database", line)
                if match:
                    findings.append({
                        "type": "SQL_INJECTION",
                        "parameter": match.group(1),
                        "dbms": match.group(2)
                    })
        return findings

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        args = command.args
        if "--batch" not in args:
            args.append("--batch")
        if "--threads" not in args:
            args.extend(["--threads", "1"])

        result = super().run(tool, command, paths)

        if result.success:
            result.findings = self._parse_output(result.output)

        return result
