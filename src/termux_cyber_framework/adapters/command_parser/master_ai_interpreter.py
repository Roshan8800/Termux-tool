import asyncio
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
import google.generativeai as genai

class MasterAIInterpreter:
    """
    A high-level interpreter that determines the user's intent by calling the
    CentralAIService. It also handles the initial, just-in-time setup of the API key,
    which is a unique responsibility of this user-facing component.
    """
    def __init__(
        self,
        ai_service: AIProcessingPort,
        config_manager: ConfigManagerAgent,
        console: Console
    ):
        self.ai_service = ai_service
        self.config_manager = config_manager
        self.console = console

        # The API key setup is still part of this agent's responsibility,
        # as it's a direct user interaction at the start of a session.
        if not self.ai_service.api_key:
             self._setup_api_key_flow()


    async def _validate_api_key(self, key: str) -> bool:
        """Tests a key with a lightweight API call."""
        try:
            # We create a temporary service to validate the key without
            # affecting the main service instance until success.
            temp_service = genai
            temp_service.configure(api_key=key)
            model = temp_service.GenerativeModel('gemini-1.5-flash')
            await model.generate_content_async("test", request_options={'timeout': 10})
            return True
        except Exception as e:
            self.console.print(f"[bold yellow]API Key validation failed:[/bold yellow] {e}")
            return False

    def _setup_api_key_flow(self) -> None:
        """Manages the user-facing flow for setting up a missing API key."""
        self.console.print("\n[bold yellow]Google Gemini API Key is not configured.[/]")
        self.console.print("This is required for all AI-powered features.")
        self.console.print("You can get a free API key at [blue underline]https://aistudio.google.com/app/apikey[/]")

        while True:
            key = Prompt.ask("[bold]Please enter your API key[/]", password=True)
            if not key:
                self.console.print("[bold red]No key entered. AI features will be disabled for this session.[/]")
                return

            with self.console.status("[bold yellow]Validating API key...[/]"):
                if asyncio.run(self._validate_api_key(key)):
                    self.console.print("[bold green]API Key is valid and has been saved.[/]")
                    self.config_manager.set_api_key("google_gemini", key)
                    # Now we can properly initialize the model in the central service
                    try:
                        genai.configure(api_key=key)
                        self.ai_service.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                        self.ai_service.api_key = key
                    except Exception as e:
                         self.console.print(f"[bold red]Error configuring Gemini API after validation: {e}[/]")
                    return
                else:
                    self.console.print("[bold red]Invalid API key. Please try again.[/]")
                    # Loop will continue

    async def interpret(self, user_input: str) -> Dict[str, Any]:
        """
        Interprets the user's natural language input by calling the CentralAIService.
        """
        if not self.ai_service.model:
            return {"intent": "error", "parameters": {"message": "MasterAIInterpreter is disabled. Please set a valid API key."}}

        return await self.ai_service.interpret_master_command(user_input)
