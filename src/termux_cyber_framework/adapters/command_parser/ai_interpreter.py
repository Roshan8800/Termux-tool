from typing import List, Dict, Any
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort, AIProcessingPort

class AIInterpreter(CommandParserPort):
    """
    A CommandParserPort implementation that uses the CentralAIService to parse commands.
    """

    def __init__(self, ai_service: AIProcessingPort, tool_catalog: List[Dict[str, Any]]):
        self.ai_service = ai_service
        self.tool_catalog = tool_catalog

    async def parse_command(self, text: str) -> Command:
        """
        Parses the given text into a structured Command by calling the CentralAIService.
        """
        try:
            return await self.ai_service.interpret_tool_command(text, self.tool_catalog)
        except Exception as e:
            # Fallback to simple parsing if the AI service fails
            print(f"AI parsing failed: {e}. Falling back to simple parsing.")
            parts = text.split()
            tool_name = parts[0]
            args = parts[1:]
            return Command(tool_name=tool_name, args=args, raw_command=text)
