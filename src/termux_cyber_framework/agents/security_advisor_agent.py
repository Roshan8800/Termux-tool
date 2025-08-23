import google.generativeai as genai
from termux_cyber_framework.core.domain.models import ExecutionResult

class SecurityAdvisorAgent:
    """
    An agent that uses an AI model to provide security advice and suggest
    next steps based on the results of a command execution.
    """
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def provide_advice(self, result: ExecutionResult) -> str:
        """
        Analyzes a successful execution result and provides advice.

        Args:
            result: The successful execution result.

        Returns:
            A string containing security advice and suggested next steps.
        """
        if not result.success or not result.output:
            return "No advice to give on a failed or empty result."

        prompt = self._build_prompt(result)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI security advisor failed: {e}"

    def _build_prompt(self, result: ExecutionResult) -> str:
        """
        Builds the prompt for the Gemini API to generate security advice.
        """
        return f"""
You are an expert-level penetration tester and security advisor.
A user has just run a cybersecurity tool and gotten a successful result.
Your task is to analyze the output and suggest the next logical step in their security assessment.

**Tool Run Details:**
- **Tool:** `{result.command.tool_name}`
- **Full Command Run:** `{' '.join([result.command.tool_name] + result.command.args)}`
- **Original User Input:** `{result.command.raw_command}`

**Tool Output (first 500 characters):**
```
{result.output[:500]}
```

**Your Task:**
1.  **Analyze the Result:** Briefly interpret what the output means.
2.  **Suggest Next Step:** Based on the output, recommend a specific and actionable next step. This could be a different tool to run or a different set of arguments for the same tool. Provide an example command if possible.

**Example Scenarios:**
- If the tool was `nmap` and it found an open web port (e.g., 80, 443), you might suggest running a web vulnerability scanner like `nikto`.
- If the tool was `whois` and it revealed an organization's IP block, you might suggest running `nmap` on that block.
- If the tool was `sqlmap` and it found a vulnerability, you might suggest trying to dump database tables.

Format your response clearly and concisely in Markdown.
"""
