import json
import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import ConsentPort

class ConsentService(ConsentPort):
    """
    A ConsentPort implementation that prompts the user for consent.
    """
    def __init__(self, log_dir="logs", log_file="consent_log.jsonl"):
        self.log_path = os.path.join(log_dir, log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def get_consent(self, command: Command) -> bool:
        """
        Prompts the user for consent and records the decision.
        """
        print(f"\nYou are about to run: {command.raw_command}")
        print("This may scan and log requests against the target.")
        response = input("Do you want to continue? [y/N] ")

        consent_given = response.lower() == "y"

        self._log_consent(command, consent_given)

        return consent_given

    def _log_consent(self, command: Command, consent_given: bool):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_command": command.raw_command,
            "interpreted_command": {
                "tool": command.tool_name,
                "args": command.args
            },
            "consent_given": consent_given
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
