from typing import Optional
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

class SecurityAdvisorAgent:
    """
    An agent that uses the Central AI Service to provide security advice and
    suggest next steps based on the results of a command execution.
    """
    def __init__(self, ai_service: AIProcessingPort):
        self.ai_service = ai_service

    async def provide_advice(self, result: ExecutionResult) -> str:
        """
        Analyzes a successful execution result and provides advice by calling
        the Central AI Service.
        """
        return await self.ai_service.summarize_execution_result(result)
