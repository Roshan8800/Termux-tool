import re
import os
import subprocess
from .generic_runner import GenericRunner
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.use_cases.ports import ToolAdapterPort

class SqlmapAdapter(GenericRunner, ToolAdapterPort):
    """
    A specific ToolAdapterPort implementation for the Sqlmap tool.
    """
    def __init__(self, command_runner: CommandRunner = None):
        super().__init__(command_runner)
        self.tool_path = "tools/sqlmap"

    def is_installed(self) -> bool:
        return os.path.exists(self.tool_path)

    def install(self, config: Config) -> bool:
        if not config.allow_system_install:
            print(f"[-] System-level installation for 'sqlmap' is not allowed by policy.")
            return False

        try:
            process = self._command_runner.run(["git", "clone", "https://github.com/sqlmapproject/sqlmap.git", self.tool_path], check=True, capture_output=True, text=True)
            return process.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
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
