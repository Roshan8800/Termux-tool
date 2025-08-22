import google.generativeai as genai
from termux_cyber_framework.core.domain.models import Command, Error

class ErrorAnalystAgent:
    """
    An agent that uses an AI model to analyze execution errors and suggest fixes.
    """
    def __init__(self, api_key: str):
        # The API key is configured here. In a real application, this should
        # be handled more securely, e.g., through a central config service.
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def analyze_error(self, command: Command, error: Error) -> str:
        """
        Analyzes a command execution error using the Gemini API.

        Args:
            command: The command that was executed.
            error: The error that occurred.

        Returns:
            A string containing an explanation of the error and a suggested fix.
        """
        prompt = self._build_prompt(command, error)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            # If the AI analysis fails, return a simple error message
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
