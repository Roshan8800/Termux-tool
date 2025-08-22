import re
import os
import subprocess
from termux_cyber_framework.adapters.tool_runner.generic_runner import GenericRunner
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

    def find_tool(self, name: str = "sqlmap"):
        if name == "sqlmap":
            return Tool(
                name="sqlmap",
                description="SQL injection tool",
                install_info=InstallInfo(method="git", source="https://github.com/sqlmapproject/sqlmap.git", path=self.tool_path),
                run_command=f"python3 {self.tool_path}/sqlmap.py"
            )
        return None

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
