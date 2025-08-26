from typing import List, Dict, Any
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

class DataCollectorAgent:
    """
    An agent that uses the Central AI Service to extract structured data
    (entities) from the output of a tool execution.
    """
    def __init__(self, ai_service: AIProcessingPort):
        self.ai_service = ai_service

    async def collect_data(self, result: ExecutionResult) -> List[Dict[str, Any]]:
        """
        Extracts structured data from an execution result by calling the
        Central AI Service.
        """
        return await self.ai_service.extract_data_from_output(result)
