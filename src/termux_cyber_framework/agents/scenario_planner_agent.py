import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional

from termux_cyber_framework.core.domain.models import Command

class ScenarioPlannerAgent:
    """
    An agent that uses an AI model to create multi-step attack scenarios
    based on a high-level user goal.
    """
    def __init__(self, api_key: Optional[str], tool_catalog: List[Dict[str, Any]]):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.tool_catalog = tool_catalog

    async def create_plan(self, goal: str) -> List[Command]:
        """
        Generates a multi-step plan to achieve a user's goal.
        """
        if not self.model:
            return [] # AI features are disabled.

        prompt = self._build_prompt(goal)

        try:
            response = await self.model.generate_content_async(prompt)
            plan_json = response.text.strip()

            # Basic cleaning for markdown code blocks
            if plan_json.startswith("```json"):
                plan_json = plan_json[7:-4].strip()

            plan_data = json.loads(plan_json)

            if not isinstance(plan_data, list) or not all(isinstance(item, dict) and "tool" in item and "args" in item for item in plan_data):
                return []

            # Convert to Command objects
            plan = [Command(tool_name=item["tool"], args=item["args"], raw_command=goal) for item in plan_data]
            return plan

        except (json.JSONDecodeError, KeyError, Exception):
            return []

    def _build_prompt(self, goal: str) -> str:
        """
        Builds the prompt for the Gemini API to create a scenario plan.
        """
        tool_descriptions = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in self.tool_catalog])

        return f"""
You are an expert cybersecurity strategist. Your task is to create a step-by-step penetration testing plan based on a user's goal and a list of available tools.

**User Goal:**
"{goal}"

**Available Tools:**
{tool_descriptions}

**Your Task:**
Create a JSON array of commands to achieve the user's goal. Each object in the array must have a "tool" (string) and "args" (list of strings) key.
Provide ONLY the JSON array. Do not include any other text or explanations.

**Example JSON Output:**
[
  {{
    "tool": "nmap",
    "args": ["-sV", "-p", "80,443", "example.com"]
  }},
  {{
    "tool": "sqlmap",
    "args": ["-u", "https://example.com/login", "--forms", "--batch"]
  }}
]

Now, create the plan for the user goal provided above.
"""
