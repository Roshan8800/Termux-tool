import json
import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class JsonReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a JSON file on the filesystem.
    """
    def __init__(self, reports_dir="reports"):
        self.reports_dir = reports_dir
        self.console = Console()
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")

        tool_name = tool_name.replace(" ", "_").replace("/", "")
        run_dir = os.path.join(self.reports_dir, date_str, tool_name)
        os.makedirs(run_dir, exist_ok=True)

        summary_path = os.path.join(run_dir, f"{time_str}.json")
        log_path = os.path.join(run_dir, f"{time_str}.log")
        return RunPaths(summary_file=summary_path, output_log_file=log_path)

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Saves the report to a JSON file and the output to a log file.
        """
        report = {
            "tool_used": result.command.tool_name,
            "command_executed": result.command.raw_command,
            "ai_interpretation": result.command.ai_interpretation,
            "execution_time": str(result.end_time - result.start_time),
            "exit_code": result.error.error_code if result.error else 0,
            "status": "Success" if result.success else "Failure",
            "error_message": result.error.message if result.error else None,
            "user_consent": result.consent_given,
            "report_generated": str(paths.summary_file),
            "output_log_file": str(paths.output_log_file),
            "output": result.output,
        }

        try:
            with open(paths.summary_file, 'w') as f:
                json.dump(report, f, indent=4)

            if paths.output_log_file:
                with open(paths.output_log_file, 'w') as f:
                    f.write(result.output)

        except Exception as e:
            self.console.print(f"[bold red]Error saving report to file: {e}[/bold red]")

        # The JSON reporter doesn't print a summary to the console,
        # as the TxtReporter already does that. We could add it if desired,
        # but it might be redundant.
        pass
