import asyncio
from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Error
from .knowledge_agent import KnowledgeAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

class ErrorAnalystAgent:
    """
    An agent that uses the Central AI Service to analyze execution errors
    and collaborates with the KnowledgeAgent for deeper insights.
    """
    def __init__(self, ai_service: AIProcessingPort, knowledge_agent: KnowledgeAgent):
        self.ai_service = ai_service
        self.knowledge_agent = knowledge_agent

    async def analyze_error(self, command: Command, error: Error) -> str:
        """
        Orchestrates the analysis of a command execution error by querying
        the AI service and the KnowledgeAgent concurrently.
        """
        # Create two tasks to run concurrently
        primary_analysis_task = self.ai_service.analyze_error(command, error)

        knowledge_query = f"What are common causes for the error '{error.message}' when using the tool '{command.tool_name}'?"
        knowledge_task = self.knowledge_agent.query(knowledge_query)

        # Await both tasks
        primary_analysis, knowledge_response = await asyncio.gather(
            primary_analysis_task,
            knowledge_task
        )

        # Combine the results
        combined_response = f"**Primary Analysis:**\n{primary_analysis}\n\n"
        if "An error occurred" not in knowledge_response and "disabled" not in knowledge_response:
             combined_response += f"**Additional Context from Knowledge Base:**\n{knowledge_response}"

        return combined_response
