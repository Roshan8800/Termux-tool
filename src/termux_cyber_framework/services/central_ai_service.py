import google.generativeai as genai
import json
from typing import List, Dict, Any, Optional

from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, Error, ExecutionResult
from termux_cyber_framework.adapters.ollama_adapter import OllamaAdapter

class CentralAIService(AIProcessingPort):
    """
    The concrete implementation of the AIProcessingPort. This service is the
    single point of contact for all AI model interactions, centralizing
    prompt engineering and model management.
    """
    def __init__(self, api_key: Optional[str], ollama_adapter: Optional[OllamaAdapter] = None):
        self.api_key = api_key
        self.ollama_adapter = ollama_adapter
        self.model = None
        if api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            except Exception:
                self.model = None

    def _build_master_prompt(self, user_input: str) -> str:
        """Builds the detailed prompt for the Gemini API."""
        return f"""
You are a master command interpreter for a cybersecurity framework. Your job is to analyze a user's natural language input and convert it into a structured JSON command.

You must identify one of the following intents:
- 'run_tool': For any request to run a specific cybersecurity tool (e.g., nmap, sqlmap, whois).
- 'update_system': For any request to update the framework or its tools.
- 'set_api_key': For any request to set or change an API key.
- 'audit_dependencies': For any request to run a dependency audit.
- 'knowledge_query': For any general question or request for information.
- 'run_pentest_analysis': For a request to start the automated PentestGPT workflow.
- 'unknown': If the intent cannot be determined.

Based on the intent, you must extract the relevant parameters.

**Output Format:**
You must respond with ONLY a valid JSON object with two keys: "intent" and "parameters".

**Examples:**

1.  **User Input:** "scan example.com for open ports using nmap"
    **Your Output:**
    ```json
    {{
      "intent": "run_tool",
      "parameters": {{
        "natural_language_command": "scan example.com for open ports using nmap"
      }}
    }}
    ```

2.  **User Input:** "start a pentest session with llama3"
    **Your Output:**
    ```json
    {{
      "intent": "run_pentest_analysis",
      "parameters": {{
        "model": "llama3"
      }}
    }}
    ```

3.  **User Input:** "set my google api key to 123-ABC-789"
    **Your Output:**
    ```json
    {{
      "intent": "set_api_key",
      "parameters": {{
        "service": "google_gemini",
        "api_key": "123-ABC-789"
      }}
    }}
    ```

Now, process the following user input.

**User Input:** "{user_input}"
**Your Output:**
"""

    async def interpret_master_command(self, user_input: str) -> Dict[str, Any]:
        """Interprets the user's master command using the Gemini API."""
        if not self.model:
            return {"intent": "error", "parameters": {"message": "AI service is not available. Check API key."}}

        prompt = self._build_master_prompt(user_input)
        try:
            response = await self.model.generate_content_async(prompt)
            cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_response_text)
        except (json.JSONDecodeError, Exception) as e:
            return {"intent": "error", "parameters": {"message": f"Failed to interpret command: {e}"}}

    def _build_tool_command_prompt(self, user_input: str, tool_catalog: List[Dict[str, Any]]) -> str:
        """Builds the prompt for the Gemini API."""
        tool_descriptions = "\n".join(
            [f"- {tool['name']}: {tool['description']}" for tool in tool_catalog]
        )

        return f"""
You are an AI assistant for a cybersecurity framework. Your task is to convert natural language commands into structured JSON commands.

Here is the catalog of available tools:
{tool_descriptions}

The user wants to execute the following command: "{user_input}"

Based on the user's intent and the available tools, choose the best tool and determine the arguments.

The output MUST be a JSON object with the following structure:
{{
  "tool": "tool_name",
  "args": ["arg1", "arg2", ...]
}}

For example:
- User input: 'check example.com for SQL injection'
- Output: {{"tool": "sqlmap", "args": ["-u", "http://example.com"]}}

- User input: 'network scan my wifi'
- Output: {{"tool": "nmap", "args": ["-sn", "192.168.1.0/24"]}}

Now, process the following user input:
User input: "{user_input}"
"""

    async def interpret_tool_command(self, user_input: str, tool_catalog: List[Dict[str, Any]]) -> Command:
        """Parses a tool command using the Gemini API."""
        if not self.model:
            raise ConnectionError("AI service is not available. Check API key.")

        prompt = self._build_tool_command_prompt(user_input, tool_catalog)
        try:
            response = await self.model.generate_content_async(prompt)
            command_json = response.text.strip()
            if command_json.startswith("```json"):
                command_json = command_json[7:-4].strip()

            command_data = json.loads(command_json)

            return Command(
                tool_name=command_data["tool"],
                args=command_data["args"],
                raw_command=user_input,
                ai_interpretation=command_data
            )
        except Exception as e:
            print(f"Central AI service failed to parse command: {e}")
            raise

    async def plan_scenario(self, goal: str) -> List[Command]:
        # TODO: Implement this method
        return []

    async def analyze_error(self, command: Command, error: Error) -> str:
        # TODO: Implement this method
        return "AI error analysis is not yet implemented."

    def _build_command_fix_prompt(self, command: Command, error: Error) -> str:
        """Builds the prompt for the Gemini API to suggest a fix."""
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

    async def suggest_command_fix(self, command: Command, error: Error) -> Optional[Command]:
        """Suggests a fix for a failed command using the Gemini API."""
        if not self.model:
            return None  # AI features disabled

        prompt = self._build_command_fix_prompt(command, error)
        try:
            response = await self.model.generate_content_async(prompt)
            command_json = response.text.strip()

            if command_json.startswith("```json"):
                command_json = command_json[7:-4].strip()

            if "NO_FIX" in command_json:
                return None

            command_data = json.loads(command_json)

            return Command(
                tool_name=command_data["tool"],
                args=command_data["args"],
                raw_command=command.raw_command # Keep original raw command
            )
        except (json.JSONDecodeError, KeyError, Exception):
            return None

    async def generate_script_patch(self, script_content: str, error: Error, command: Command) -> str:
        # TODO: Implement this method
        return ""

    def _build_knowledge_question_prompt(self, question: str, tool_context: Optional[str] = None) -> str:
        """Builds the prompt for a knowledge base question."""
        tool_context_prompt = ""
        if tool_context:
            tool_context_prompt = f"The user's question is specifically about the '{tool_context}' tool. Prioritize your answer based on its official documentation, common usage patterns, and best practices."

        return f"""
You are a world-class cybersecurity expert and senior penetration tester.
Your task is to answer the following user question about a cybersecurity tool or concept.
{tool_context_prompt}
Provide a clear, concise, and accurate answer.
If the question is about how to use a tool, provide an example command.
If possible, include 1-2 high-quality reference links (e.g., official documentation, well-known blogs) at the end of your answer.
User Question: "{question}"
Answer:
"""

    async def answer_knowledge_question(self, question: str, tool_context: Optional[str] = None) -> str:
        """Answers a knowledge-based question using the Gemini API."""
        if not self.model:
            return "Knowledge Agent is disabled because no API key was provided."

        prompt = self._build_knowledge_question_prompt(question, tool_context)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"An error occurred while querying the knowledge base: {e}"

    async def extract_data_from_output(self, result: ExecutionResult) -> List[Dict[str, Any]]:
        # TODO: Implement this method
        return []

    def _build_security_advice_prompt(self, result: ExecutionResult) -> str:
        """Builds the prompt for the Gemini API to generate security advice."""
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

    async def summarize_execution_result(self, result: ExecutionResult) -> str:
        """Generates a security-focused summary and advice based on a tool's execution result."""
        if not self.model:
            return "AI security advisor is disabled because no API key was provided."

        if not result.success or not result.output:
            return "No advice to give on a failed or empty result."

        prompt = self._build_security_advice_prompt(result)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI security advisor failed: {e}"
