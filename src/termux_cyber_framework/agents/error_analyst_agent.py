import google.generativeai as genai
from typing import Optional
import asyncio
from termux_cyber_framework.core.domain.models import Command, Error
from .knowledge_agent import KnowledgeAgent

class ErrorAnalystAgent:
    """
    An agent that uses an AI model to analyze execution errors and suggest fixes.
    It collaborates with the KnowledgeAgent for deeper insights.
    """
    def __init__(self, api_key: Optional[str], knowledge_agent: KnowledgeAgent):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.knowledge_agent = knowledge_agent

    async def analyze_error(self, command: Command, error: Error) -> str:
        """
        Analyzes a command execution error using the Gemini API and enriches
        it with information from the KnowledgeAgent.
        """
        if not self.model:
            return "AI error analysis is disabled because no API key was provided."

        # Create two tasks to run concurrently
        primary_analysis_task = self._get_primary_analysis(command, error)
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

    async def _get_primary_analysis(self, command: Command, error: Error) -> str:
        """Gets the initial analysis from the primary model."""
        prompt = self._build_prompt(command, error)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI error analysis failed: {e}"

    def _build_prompt(self, command: Command, error: Error) -> str:
        """
        Builds the prompt for the Gemini API to analyze an error.
        """
        return f"""
You are an expert-level cybersecurity assistant and command-line tool troubleshooter.
A user in a Termux/Linux environment tried to run a command and it failed.
Your task is to analyze the error and provide a clear, concise explanation and a suggested fix.

**Command Details:**
- **Tool:** `{command.tool_name}`
- **Full Command Run:** `{' '.join([command.tool_name] + command.args)}`
- **Original User Input:** `{command.raw_command}`

**Error Details:**
- **Exit Code:** `{error.error_code}`
- **Error Message / Stderr:**
```
{error.message}
```

**Your Task:**
1.  **Explain the Error:** In simple terms, what does this error mean? Why did it likely happen?
2.  **Suggest a Fix:** Provide a concrete command or action the user should take to fix the problem. If you suggest a command, provide the exact command to run.

Format your response clearly in Markdown.
"""
