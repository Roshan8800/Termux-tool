import json
import re
from typing import List
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort

class RulesParserAdapter(CommandParserPort):
    """
    A CommandParserPort implementation that uses regex rules to parse commands.
    """
    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: str) -> List[dict]:
        with open(path, 'r') as f:
            return json.load(f)

    async def parse_command(self, text: str) -> Command:
        for rule in self.rules:
            match = re.search(rule["pattern"], text, re.IGNORECASE)
            if match:
                groups = match.groups()
                tool_name = rule["tool_name"]
                args = []
                for i, group in enumerate(groups):
                    if group:
                        args.append(group)
                return Command(tool_name=tool_name, args=args, raw_command=text)

        # Fallback to simple parsing
        parts = text.split()
        tool_name = parts[0]
        args = parts[1:]
        return Command(tool_name=tool_name, args=args, raw_command=text)
