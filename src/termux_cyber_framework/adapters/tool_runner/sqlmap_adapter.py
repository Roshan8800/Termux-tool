import re
from .generic_runner import GenericRunner
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult

class SqlmapAdapter(GenericRunner):
    """
    A specific ToolRunnerPort implementation for the Sqlmap tool.
    """
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

    def run(self, tool: Tool, command: Command) -> ExecutionResult:
        args = command.args
        if "--batch" not in args:
            args.append("--batch")
        if "--threads" not in args:
            args.extend(["--threads", "1"])

        result = super().run(tool, command)

        if result.success:
            result.findings = self._parse_output(result.output)

        return result
