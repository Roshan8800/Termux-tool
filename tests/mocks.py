import subprocess
import os
from typing import List, Optional

from termux_cyber_framework.core.use_cases.ports import ConsentPort
from termux_cyber_framework.core.domain.models import Command

from termux_cyber_framework.core.use_cases.ports import AuditLoggerPort, CommandParserPort


class MockAIInterpreter(CommandParserPort):
    def __init__(self, *args, **kwargs):
        pass

    async def parse_command(self, text: str) -> Command:
        parts = text.split()
        tool_name = parts[0]
        args = parts[1:]
        return Command(
            tool_name=tool_name,
            args=args,
            raw_command=text,
            ai_interpretation={"tool": tool_name, "args": args}
        )

    async def interpret(self, text: str) -> dict:
        """Mocks the MasterAIInterpreter's interpret method."""
        return {
            "intent": "run_tool",
            "parameters": {"natural_language_command": text}
        }

class MockAuditLogger(AuditLoggerPort):
    def __init__(self):
        self.events = []

    def append(self, event: dict) -> None:
        self.events.append(event)

class MockInstallLogger:
    def __init__(self, log_dir="logs"):
        self.logs = {}

    def log(self, tool_name: str, content: str):
        if tool_name not in self.logs:
            self.logs[tool_name] = []
        if content:
            self.logs[tool_name].append(content)

from termux_cyber_framework.core.domain.models import ExecutionResult

class MockExecutionHistory:
    def __init__(self):
        self.history = []

    def append(self, result: ExecutionResult):
        self.history.append(result)

class MockSecurityComplianceAgent(ConsentPort):
    def __init__(self, consent_to_give: bool = True):
        self.consent_to_give = consent_to_give

    def get_consent(self, command: Command) -> bool:
        return self.consent_to_give

class MockCommandRunner:
    """
    A mock command runner that can be used in tests.
    """
    def __init__(self, mock_results: Optional[dict] = None):
        self.mock_results = mock_results or {}
        self.call_count = 0
        self.last_command = None

    def run(self, command: List[str], **kwargs):
        self.call_count += 1
        self.last_command = command
        if isinstance(command, list):
            command_str = " ".join(command)
        else:
            command_str = command

        print(f"DEBUG: MockCommandRunner: command_str='{command_str}', mock_results={self.mock_results}")

        if command_str in self.mock_results:
            result = self.mock_results[command_str]
            if "exception" in result:
                raise result["exception"]

            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")

            if 'output_log_file' in kwargs:
                log_file = kwargs['output_log_file']
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir) and log_dir:
                    os.makedirs(log_dir)
                with open(log_file, "w") as f:
                    f.write(f"--- Running command: {command_str} ---\n")
                    f.write(f"\n--- STDOUT ---\n{stdout}")
                    f.write(f"\n--- STDERR ---\n{stderr}")

            process = subprocess.CompletedProcess(
                args=command,
                returncode=result.get("returncode", 0),
                stdout=stdout,
                stderr=stderr,
            )
            process.pid = 1234
            return process

        process = subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )
        process.pid = 1234
        return process


class MockErrorAnalystAgent:
    async def analyze_error(self, command: Command, error) -> str:
        return "Mock AI analysis of the error."

class MockErrorFixerAgent:
    async def suggest_fix(self, command: Command, error) -> Optional[Command]:
        return None # Default to no fix

class MockToolInstallerAgent:
    def __init__(self):
        self.install_if_needed_called = False
        self.install_if_needed_tool = None

    def install_if_needed(self, tool):
        self.install_if_needed_called = True
        self.install_if_needed_tool = tool
