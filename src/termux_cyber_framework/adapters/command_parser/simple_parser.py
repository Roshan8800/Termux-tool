from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort

class SimpleCommandParserAdapter(CommandParserPort):
    """
    A simple, non-AI command parser that splits the input string.
    This serves as a placeholder for a more sophisticated AI parser.
    """
    async def parse_command(self, text: str) -> Command:
        """
        Parses the input text by splitting it into words.
        The first word is assumed to be the tool name.

        Args:
            text: The raw user input string.

        Returns:
            A Command object.

        Raises:
            ValueError: If the input command is empty.
        """
        parts = text.strip().split()
        if not parts:
            raise ValueError("Cannot parse an empty command.")

        tool_name = parts[0]
        args = parts[1:]

        return Command(
            tool_name=tool_name,
            args=args,
            raw_command=text
        )
