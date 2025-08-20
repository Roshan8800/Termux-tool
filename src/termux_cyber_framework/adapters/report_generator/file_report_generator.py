import os
import json
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort

class FileReportGenerator(ReportGeneratorPort):
    """
    An adapter that saves the execution report to a JSON file.
    """
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate(self, result: ExecutionResult) -> None:
        """
        Saves the given report to a file in the reports directory.
        The filename includes the tool name and a timestamp.

        Args:
            result: The execution result to be saved.
        """
        timestamp = result.end_time.strftime('%Y%m%d%H%M%S')
        tool_name = result.command.tool_name
        # Sanitize tool_name for the filename
        safe_tool_name = "".join(c for c in tool_name if c.isalnum() or c in ('_', '-')).rstrip()

        filename = f"{safe_tool_name}-{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)

        try:
            # Use Pydantic's model_dump_json for clean serialization
            with open(filepath, 'w') as f:
                f.write(result.model_dump_json(indent=4))

            # Also print a summary to the console for immediate feedback
            print(f"\n--- Execution Report ---")
            print(f"[*] Command: {result.command.raw_command}")
            print(f"[*] Success: {result.success}")
            if result.success:
                print(f"[*] Output:\n{result.output[:500]}...") # Print first 500 chars
            else:
                print(f"[*] Error:\n{result.error.message}")
            print(f"[+] Report saved to: {filepath}")

        except Exception as e:
            print(f"Error saving report to file: {e}")
