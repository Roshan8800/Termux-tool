import re
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort

class RegexCommandParserAdapter(CommandParserPort):
    """
    A command parser that uses regular expressions to extract the tool and arguments.
    This offers a more robust parsing mechanism than a simple string split.
    """
    # This regex captures the first word (the tool) and the rest of the string (the args).
    # It is designed to be simple and effective for standard command-line syntax.
    COMMAND_PATTERN = re.compile(r"^\s*(?P<tool>[a-zA-Z0-9_-]+)\s*(?P<args>.*)$")

    async def parse_command(self, text: str) -> Command:
        """
        Parses the input text using a regular expression to separate the tool
        from its arguments.

        Args:
            text: The raw user input string.

        Returns:
            A structured Command object.

        Raises:
            ValueError: If the command format is invalid.
        """
        match = self.COMMAND_PATTERN.match(text.strip())

        if not match:
            # This could happen if the user only enters symbols or an empty string
            raise ValueError(f"Could not parse command: '{text}'. Expected format: <tool> [args...]")

        tool_name = match.group("tool")

        # The rest of the string is treated as arguments
        args_str = match.group("args").strip()
        # We still split the args string to get a list of individual arguments
        args = args_str.split() if args_str else []

        return Command(
            tool_name=tool_name,
            args=args,
            raw_command=text
        )
