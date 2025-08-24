import json
import os
from typing import List
import google.generativeai as genai
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import CommandParserPort

class AIInterpreter(CommandParserPort):
    """
    A CommandParserPort implementation that uses an AI to parse commands.
    """

    def __init__(self, tool_catalog_path: str, api_key: str):
        if not api_key:
            raise ValueError("API key for AIInterpreter is required.")
        genai.configure(api_key=api_key)
        self.tool_catalog = self._load_tool_catalog(tool_catalog_path)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def _load_tool_catalog(self, path: str) -> List[dict]:
        with open(path, 'r') as f:
            return json.load(f)

    async def parse_command(self, text: str) -> Command:
        """
        Parses the given text into a structured Command using the Gemini API.
        """
        prompt = self._build_prompt(text)
        try:
            response = await self.model.generate_content_async(prompt)

            # The response is expected to be a JSON string
            command_json = response.text.strip()
            # It's good practice to remove markdown code block delimiters
            if command_json.startswith("```json"):
                command_json = command_json[7:-4].strip()

            command_data = json.loads(command_json)

            return Command(
                tool_name=command_data["tool"],
                args=command_data["args"],
                raw_command=text,
                ai_interpretation=command_data
            )
        except Exception as e:
            # Fallback to simple parsing if the AI fails
            print(f"AI parsing failed: {e}. Falling back to simple parsing.")
            parts = text.split()
            tool_name = parts[0]
            args = parts[1:]
            return Command(tool_name=tool_name, args=args, raw_command=text)


    def _build_prompt(self, user_input: str) -> str:
        """
        Builds the prompt for the Gemini API.
        """
        tool_descriptions = "\n".join(
            [f"- {tool['name']}: {tool['description']}" for tool in self.tool_catalog]
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
