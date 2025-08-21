import json
import re
import os
from datetime import datetime
from typing import List
from termux_cyber_framework.core.domain.models import Remediation, Command, Error
from termux_cyber_framework.core.use_cases.ports import DoctorPort, LoggerPort
from termux_cyber_framework.core.command_runner import CommandRunner

class RegexDoctorAdapter(DoctorPort):
    """
    A DoctorPort implementation that uses regex rules to detect and fix issues.
    """
    def __init__(self, rules_path: str, command_runner: CommandRunner = None, logger: LoggerPort = None, log_dir="logs"):
        self.rules = self._load_rules(rules_path)
        self._command_runner = command_runner or CommandRunner()
        self._logger = logger
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _load_rules(self, path: str) -> List[dict]:
        with open(path, 'r') as f:
            return json.load(f)

    def diagnose(self, error: Error, command: Command) -> list[Remediation]:
        remediations = []
        for rule in self.rules:
            if re.search(rule["pattern"], error.message, re.IGNORECASE):
                for fix_command_str in rule["commands"]:
                    # This is a simplification. A real implementation would need a more robust way
                    # to construct the new command, potentially using the original command as context.
                    new_command = Command(
                        tool_name=fix_command_str.split()[0],
                        args=fix_command_str.split()[1:],
                        raw_command=fix_command_str
                    )
                    remediation = Remediation(
                        description=rule["explain"],
                        command=new_command
                    )
                    remediations.append(remediation)
                    self._log_remediation(remediation)
        return remediations

    def _log_remediation(self, remediation: Remediation):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file = os.path.join(self.log_dir, f"doctor-{timestamp}.jsonl")
        with open(log_file, "a") as f:
            f.write(remediation.model_dump_json() + "\n")

        if self._logger:
            self._logger.log(f"Doctor remediation proposed: {remediation.description}", level="INFO")
