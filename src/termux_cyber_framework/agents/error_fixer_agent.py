import google.generativeai as genai
import json
from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Error

class ErrorFixerAgent:
    """
    An agent that uses an AI model to suggest a runnable command to fix an error.
    """
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def suggest_fix(self, command: Command, error: Error) -> Optional[Command]:
        """
        Analyzes an error and suggests a new, corrected command.

        Args:
            command: The original command that failed.
            error: The error that occurred.

        Returns:
            A new Command object with a suggested fix, or None if no fix
            can be determined.
        """
        prompt = self._build_prompt(command, error)
        try:
            response = await self.model.generate_content_async(prompt)
            command_json = response.text.strip()

            # It's good practice to remove markdown code block delimiters
            if command_json.startswith("```json"):
                command_json = command_json[7:-4].strip()

            if "NO_FIX" in command_json:
                return None

            command_data = json.loads(command_json)

            # The new command should inherit the original raw_command for context
            return Command(
                tool_name=command_data["tool"],
                args=command_data["args"],
                raw_command=command.raw_command
            )
        except (json.JSONDecodeError, KeyError, Exception):
            # If AI fails or returns invalid format, return no fix.
            return None

    def _build_prompt(self, command: Command, error: Error) -> str:
        """
        Builds the prompt for the Gemini API to suggest a fix.
        """
        return f"""
You are an expert-level command-line tool troubleshooter. A user's command failed. Your task is to provide a machine-readable, runnable command to fix the issue.

**Failed Command Details:**
- **Tool:** `{command.tool_name}`
- **Full Command Run:** `{' '.join([command.tool_name] + command.args)}`

**Error Details:**
- **Exit Code:** `{error.error_code}`
- **Error Message / Stderr:**
```
{error.message}
```

**Your Task:**
Analyze the error and determine a new command that will fix the problem. The fix might involve using a different tool (like `sudo`), adding or changing arguments, or correcting a typo.

**Output Format:**
- If you can determine a fix, provide ONLY a JSON object with the new command's tool name and arguments. The JSON object MUST have this exact structure:
  `{{"tool": "tool_name", "args": ["arg1", "arg2", ...]}}`
- If you cannot determine a fix or if no fix is necessary, output only the string `NO_FIX`.

**Example Scenarios:**
- **Scenario 1 (Permission Denied):**
  - **Failed Command:** `nmap -p 80 localhost`
  - **Error:** `Permission denied`
  - **Your Output:** `{{"tool": "sudo", "args": ["nmap", "-p", "80", "localhost"]}}`

- **Scenario 2 (Missing Dependency):**
  - **Failed Command:** `nikto -h example.com`
  - **Error:** `bash: nikto: command not found`
  - **Your Output:** `{{"tool": "apt-get", "args": ["install", "nikto", "-y"]}}`

- **Scenario 3 (No Obvious Fix):**
  - **Failed Command:** `nmap -sV 127.0.0.1`
  - **Error:** `Host seems down.`
  - **Your Output:** `NO_FIX`

Now, process the failed command detailed above.
"""
