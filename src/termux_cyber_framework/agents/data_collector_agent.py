import json
import threading
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional

from termux_cyber_framework.core.domain.models import ExecutionResult

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataCollectorAgent:
    """
    An agent responsible for collecting, structuring, and storing data from tool executions.
    """
    def __init__(self, api_key: Optional[str], findings_path: str = "data/findings.json"):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.findings_path = findings_path
        self._lock = threading.Lock()
        self._initialize_findings_file()

    def _initialize_findings_file(self):
        """Ensures the findings file exists and is a valid JSON list."""
        with self._lock:
            try:
                import os
                os.makedirs(os.path.dirname(self.findings_path), exist_ok=True)

                with open(self.findings_path, 'r') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("Findings file is not a list.")
            except (FileNotFoundError, json.JSONDecodeError, ValueError):
                with open(self.findings_path, 'w') as f:
                    json.dump([], f)

    def _read_findings(self) -> List[Dict[str, Any]]:
        """Reads all findings from the JSON file in a thread-safe manner."""
        with self._lock:
            with open(self.findings_path, 'r') as f:
                return json.load(f)

    def _append_findings(self, new_findings: List[Dict[str, Any]]):
        """Appends a list of new findings to the JSON file in a thread-safe manner."""
        if not new_findings:
            return

        with self._lock:
            with open(self.findings_path, 'r+') as f:
                data = json.load(f)
                data.extend(new_findings)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()

    async def process_and_store_result(self, result: ExecutionResult):
        """
        Processes the raw output from an execution result, extracts structured data,
        and appends it to the findings data store.
        """
        if not self.model:
            return

        structured_findings = await self._extract_data(result)
        if structured_findings:
            self._append_findings(structured_findings)
            logging.info(f"--- DataCollectorAgent: Stored {len(structured_findings)} new findings from '{result.command.tool_name}'. ---")

    def _build_extraction_prompt(self, tool_name: str, raw_output: str) -> str:
        """Builds a specialized prompt for extracting data from a tool's output."""
        return f"""
You are a data extraction specialist. Your task is to parse the raw output from a cybersecurity tool and extract key findings into a structured JSON format.

**Tool:**
"{tool_name}"

**Raw Output:**
```
{raw_output}
```

**Your Task:**
Analyze the output and extract all significant findings (like open ports, vulnerabilities, discovered subdomains, etc.).
- Output the result as a JSON array of objects.
- Each object should represent a single finding and contain key-value pairs.
- If no significant findings are present, return an empty JSON array `[]`.
- Provide ONLY the JSON array.
"""

    async def _extract_data(self, result: ExecutionResult) -> Optional[List[Dict[str, Any]]]:
        """
        Uses an AI model to extract structured data from raw tool output.
        """
        prompt = self._build_extraction_prompt(result.command.tool_name, result.output)

        try:
            response = await self.model.generate_content_async(prompt)
            json_text = response.text.strip()

            if json_text.startswith("```json"):
                json_text = json_text[7:-4].strip()

            findings = json.loads(json_text)

            if isinstance(findings, list):
                return findings
            else:
                logging.warning(f"--- DataCollectorAgent: AI returned valid JSON, but it was not a list for tool '{result.command.tool_name}'. ---")
                return None

        except json.JSONDecodeError:
            logging.warning(f"--- DataCollectorAgent: AI returned malformed JSON for tool '{result.command.tool_name}'. Skipping data extraction. ---")
            return None
        except Exception as e:
            logging.error(f"--- DataCollectorAgent: An unexpected error occurred during data extraction: {e} ---")
            return None
