import google.generativeai as genai
import json
import asyncio
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent

class MasterAIInterpreter:
    """
    A high-level interpreter that uses an AI model to determine the user's
    intent and also handles the initial, just-in-time setup of the API key.
    """
    def __init__(
        self,
        api_key: Optional[str],
        config_manager: ConfigManagerAgent,
        console: Console
    ):
        self.model = None
        self.api_key = api_key
        self.config_manager = config_manager
        self.console = console

        if not self.api_key or self.api_key == "dummy_key_for_testing":
            self.api_key = self._setup_api_key_flow()

        self._initialize_model()

    def _initialize_model(self):
        """Initializes the Gemini model."""
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                self.console.print(f"[bold red]Error configuring Gemini API: {e}[/]")
                self.model = None

    async def _validate_api_key(self, key: str) -> bool:
        """Tests a key with a lightweight API call."""
        try:
            temp_genai = genai
            temp_genai.configure(api_key=key)
            model = temp_genai.GenerativeModel('gemini-1.5-flash')
            await model.generate_content_async("test", request_options={'timeout': 10})
            # Restore original configuration if it existed
            if self.api_key and self.api_key != "dummy_key_for_testing":
                 genai.configure(api_key=self.api_key)
            return True
        except Exception as e:
            self.console.print(f"[bold yellow]API Key validation failed:[/bold yellow] {e}")
            return False

    def _setup_api_key_flow(self) -> Optional[str]:
        """Manages the user-facing flow for setting up a missing API key."""
        self.console.print("\n[bold yellow]Google Gemini API Key is not configured.[/]")
        self.console.print("This is required for all AI-powered features.")
        self.console.print("You can get a free API key at [blue underline]https://aistudio.google.com/app/apikey[/]")

        while True:
            key = Prompt.ask("[bold]Please enter your API key[/]", password=True)
            if not key:
                self.console.print("[bold red]No key entered. AI features will be disabled.[/]")
                return None

            with self.console.status("[bold yellow]Validating API key...[/]"):
                if asyncio.run(self._validate_api_key(key)):
                    self.console.print("[bold green]API Key is valid and has been saved.[/]")
                    self.config_manager.set_api_key("google_gemini", key)
                    return key
                else:
                    self.console.print("[bold red]Invalid API key. Please try again.[/]")
                    # Loop will continue

    async def interpret(self, user_input: str) -> Dict[str, Any]:
        """
        Interprets the user's natural language input to determine their
        intent and extract relevant parameters.
        """
        if not self.model:
            return {"intent": "error", "parameters": {"message": "MasterAIInterpreter is disabled. Please set a valid API key."}}

        prompt = self._build_prompt(user_input)
        try:
            response = await self.model.generate_content_async(prompt)
            cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            parsed_response = json.loads(cleaned_response_text)
            return parsed_response
        except (json.JSONDecodeError, Exception) as e:
            return {"intent": "error", "parameters": {"message": f"Failed to interpret command: {e}"}}

    def _build_prompt(self, user_input: str) -> str:
        """Builds the detailed prompt for the Gemini API."""
        # The prompt remains the same as before
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
