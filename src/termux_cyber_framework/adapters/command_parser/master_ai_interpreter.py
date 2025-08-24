import google.generativeai as genai
import json
from typing import Optional, Dict, Any

class MasterAIInterpreter:
    """
    A high-level interpreter that uses an AI model to determine the user's
    intent and extract parameters from pure natural language.
    """
    def __init__(self, api_key: Optional[str]):
        self.model = None
        if api_key:
            # In a real app, genai.configure would be called once.
            # For this agent, we assume it's configured externally or here.
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                # Handle cases where the API key is invalid on configuration
                self.model = None

    async def interpret(self, user_input: str) -> Dict[str, Any]:
        """
        Interprets the user's natural language input to determine their
        intent and extract relevant parameters.

        Returns:
            A dictionary containing the 'intent' and associated 'parameters'.
        """
        if not self.model:
            return {"intent": "error", "parameters": {"message": "MasterAIInterpreter is disabled, API key not provided or invalid."}}

        prompt = self._build_prompt(user_input)
        try:
            response = await self.model.generate_content_async(prompt)
            # Clean up the response text before parsing
            cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            parsed_response = json.loads(cleaned_response_text)
            return parsed_response
        except (json.JSONDecodeError, Exception) as e:
            return {"intent": "error", "parameters": {"message": f"Failed to interpret command: {e}"}}

    def _build_prompt(self, user_input: str) -> str:
        """Builds the detailed prompt for the Gemini API."""
        return f"""
You are a master command interpreter for a cybersecurity framework. Your job is to analyze a user's natural language input and convert it into a structured JSON command.

You must identify one of the following intents:
- 'run_tool': For any request to run a specific cybersecurity tool (e.g., nmap, sqlmap, whois).
- 'update_system': For any request to update the framework or its tools.
- 'set_api_key': For any request to set or change an API key.
- 'audit_dependencies': For any request to run a dependency audit.
- 'knowledge_query': For any general question or request for information.
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

2.  **User Input:** "update the framework and all my tools"
    **Your Output:**
    ```json
    {{
      "intent": "update_system",
      "parameters": {{}}
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

4.  **User Input:** "are there any conflicts in my python environment?"
    **Your Output:**
    ```json
    {{
      "intent": "audit_dependencies",
      "parameters": {{}}
    }}
    ```

5.  **User Input:** "how do i use sqlmap to scan for time-based blind injection?"
    **Your Output:**
    ```json
    {{
      "intent": "knowledge_query",
      "parameters": {{
        "question": "how do i use sqlmap to scan for time-based blind injection?"
      }}
    }}
    ```

Now, process the following user input.

**User Input:** "{user_input}"
**Your Output:**
"""
