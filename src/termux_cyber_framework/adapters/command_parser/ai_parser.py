import re
from typing import Dict, List, Tuple
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort

class AICommandParserAdapter(CommandParserPort):
    """
    A simulated AI/NLP parser that uses keyword matching and regex to interpret
    natural language commands.
    """
    def __init__(self):
        self.tool_keywords: Dict[str, List[str]] = {
            "nmap": ["nmap", "scan", "port scan", "network scan", "discover hosts"],
            "sqlmap": ["sqlmap", "sql injection", "database vulnerability"],
            "whois": ["whois", "domain owner", "lookup domain"],
        }
        # Prepositions and common stop words to be removed from argument parsing
        self.stop_words = {"with", "on", "for", "at", "the", "a", "an", "of", "to"}

    def _find_tool(self, text: str) -> Tuple[str, str]:
        """Finds the tool and returns the tool name and the remaining text."""
        text_lower = text.lower()
        for tool_name, keywords in self.tool_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Remove the keyword to help with arg parsing
                    remaining_text = text_lower.replace(keyword, "").strip()
                    return tool_name, remaining_text
        # As a fallback, assume the first word is the tool
        parts = text.split()
        return parts[0], " ".join(parts[1:])

    def _extract_args(self, text: str) -> List[str]:
        """Extracts arguments from the remaining text."""
        # A simple regex to find potential hostnames, IPs, and file paths
        # This is a simplification and could be much more robust.
        potential_args = re.findall(r"[\w.-]+", text)

        # Filter out any remaining stop words
        args = [arg for arg in potential_args if arg.lower() not in self.stop_words]
        return args

    async def parse_command(self, text: str) -> Command:
        """
        Parses the natural language input to identify a tool and its arguments.

        Example: "scan target.com with nmap" -> Command(tool_name="nmap", args=["target.com"])
        """
        if not text.strip():
            raise ValueError("Cannot parse an empty command.")

        tool_name, remaining_text = self._find_tool(text)
        args = self._extract_args(remaining_text)

        return Command(
            tool_name=tool_name,
            args=args,
            raw_command=text
        )
