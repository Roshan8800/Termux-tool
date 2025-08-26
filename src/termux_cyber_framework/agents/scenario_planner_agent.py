from typing import List
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

class ScenarioPlannerAgent:
    """
    An agent that uses the Central AI Service to create a multi-step
    attack plan based on a high-level goal.
    """
    def __init__(self, ai_service: AIProcessingPort):
        self.ai_service = ai_service

    async def plan_attack_scenario(self, goal: str) -> List[Command]:
        """
        Generates a multi-step attack plan by calling the Central AI Service.
        """
        return await self.ai_service.plan_scenario(goal)
