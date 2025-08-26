from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Error
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

class ErrorFixerAgent:
    """
    An agent that uses the Central AI Service to suggest a runnable command to fix an error.
    """
    def __init__(self, ai_service: AIProcessingPort):
        self.ai_service = ai_service

    async def suggest_fix(self, command: Command, error: Error) -> Optional[Command]:
        """
        Analyzes an error and suggests a new, corrected command by calling the CentralAIService.
        """
        return await self.ai_service.suggest_command_fix(command, error)
