import google.generativeai as genai
from typing import Optional
import ast
import subprocess
import logging

from termux_cyber_framework.core.domain.models import Command, Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoEditorAgent:
    """
    An agent that uses an AI model to automatically patch broken tool scripts.
    """
    def __init__(self, api_key: Optional[str]):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def patch_script(self, script_path: str, error: Error, command: Command) -> bool:
        """
        Attempts to read, patch, validate, and save a broken script.
        """
        logging.info(f"--- AutoEditorAgent: Starting patch for {script_path} ---")
        if not self.model:
            logging.warning("--- AutoEditorAgent: Model not available, aborting. ---")
            return False

        try:
            with open(script_path, 'r') as f:
                original_content = f.read()
        except FileNotFoundError:
            logging.error(f"--- AutoEditorAgent: File not found: {script_path} ---")
            return False

        prompt = self._build_prompt(original_content, error, command)

        try:
            response = await self.model.generate_content_async(prompt)
            patched_content = response.text.strip()
            logging.info(f"--- AutoEditorAgent: Raw AI response: {patched_content[:200]}... ---")
            if patched_content.startswith("```"):
                code_start = patched_content.find('\n') + 1
                code_end = patched_content.rfind('```')
                if code_end > code_start:
                    patched_content = patched_content[code_start:code_end].strip()
            logging.info(f"--- AutoEditorAgent: Cleaned patch content: {patched_content[:200]}... ---")
        except Exception as e:
            logging.error(f"--- AutoEditorAgent: AI call failed: {e} ---")
            return False

        is_valid = self._validate_patch(patched_content, script_path)
        logging.info(f"--- AutoEditorAgent: Patch validation result for {script_path}: {is_valid} ---")
        if not is_valid:
            return False

        try:
            with open(script_path, 'w') as f:
                f.write(patched_content)
            logging.info(f"--- AutoEditorAgent: Successfully wrote patch to {script_path} ---")
            return True
        except IOError as e:
            logging.error(f"--- AutoEditorAgent: Failed to write file {script_path}: {e} ---")
            return False

    def _validate_patch(self, script_content: str, script_path: str) -> bool:
        """
        Validates the syntax of the patched script content.
        """
        if not script_content:
            return False

        if '.' in script_path:
            file_extension = script_path.split('.')[-1]
        else:
            file_extension = 'sh'

        logging.info(f"--- AutoEditorAgent: Validating as type '{file_extension}' ---")

        if file_extension == 'py':
            try:
                ast.parse(script_content)
                return True
            except SyntaxError as e:
                logging.warning(f"--- AutoEditorAgent: Python syntax validation failed: {e} ---")
                return False
        elif file_extension == 'sh':
            try:
                process = subprocess.run(
                    ["shellcheck", "-s", "sh", "-"],
                    input=script_content, text=True, capture_output=True, check=False
                )
                if process.returncode not in [0, 1]:
                    logging.warning(f"--- AutoEditorAgent: Shellcheck validation failed with code {process.returncode}: {process.stderr} ---")
                return process.returncode in [0, 1]
            except FileNotFoundError:
                logging.warning("--- AutoEditorAgent: shellcheck not found, skipping validation. ---")
                return True
            except Exception as e:
                logging.error(f"--- AutoEditorAgent: Exception during shellcheck validation: {e} ---")
                return False

        return True

    def _build_prompt(self, script_content: str, error: Error, command: Command) -> str:
        """
        Builds the prompt for the Gemini API to patch a script.
        """
        return f"""
You are an expert-level software engineer specializing in debugging and patching code.
A user in a Termux/Linux environment tried to run a command that executed a script, and the script failed.
Your task is to analyze the script and the error it produced, and provide a corrected, complete version of the script.

**Command that Failed:**
`{' '.join([command.tool_name] + command.args)}`

**Error Message (stderr):**
```
{error.message}
```

**Full Content of the Broken Script (`{command.tool_name}`):**
```
{script_content}
```

**Your Task:**
Rewrite the entire script to fix the error.
-   Do NOT provide any commentary, explanations, or code diffs.
-   Provide ONLY the full, corrected script content, inside a single code block.
-   Ensure the corrected script is complete and runnable.
"""
