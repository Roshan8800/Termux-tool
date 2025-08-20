import json
import re
import os
from datetime import datetime
from typing import List
from termux_cyber_framework.core.domain.models import ExecutionResult
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

    async def detect_and_fix(self, result: ExecutionResult) -> List[dict]:
        fixes = []
        for rule in self.rules:
            if re.search(rule["pattern"], result.output, re.IGNORECASE) or \
               (result.error and re.search(rule["pattern"], result.error.message, re.IGNORECASE)):

                fix = {
                    "id": rule["id"],
                    "explain": rule["explain"],
                    "commands": rule["commands"],
                    "status": "pending_user_confirm"
                }

                if not rule["require_confirm"]:
                    # For now, we assume the policy allows auto-fix.
                    # A more robust implementation would check a config flag.
                    for command in rule["commands"]:
                        self._command_runner.run(command.split())
                    fix["status"] = "applied"

                self._log_fix(fix)
                fixes.append(fix)
        return fixes

    def _log_fix(self, fix: dict):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file = os.path.join(self.log_dir, f"doctor-{timestamp}.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(fix) + "\n")

        if self._logger:
            self._logger.log(f"Doctor fix proposed: {fix['id']}", level="INFO")
