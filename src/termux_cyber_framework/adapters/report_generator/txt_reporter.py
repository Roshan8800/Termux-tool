import os
import json
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class TxtReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a text file on the filesystem.
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

        summary_path = os.path.join(run_dir, f"{time_str}.txt")
        log_path = os.path.join(run_dir, f"{time_str}.log")
        return RunPaths(summary_file=summary_path, output_log_file=log_path)

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Saves the report to a text file and the output to a log file.
        """
        try:
            with open(paths.summary_file, 'w') as f:
                f.write("--- Execution Report ---\n")
                f.write(f"Tool Used: {result.command.tool_name}\n")
                f.write(f"Command Executed: {result.command.raw_command}\n")
                if result.command.ai_interpretation:
                    f.write(f"AI Interpretation: {json.dumps(result.command.ai_interpretation)}\n")
                f.write(f"Execution Time: {result.end_time - result.start_time}\n")
                f.write(f"Exit Code: {result.error.error_code if result.error else 0}\n")
                f.write(f"Status: {'Success' if result.success else 'Failure'}\n")
                if result.error:
                    f.write(f"Error Message: {result.error.message}\n")
                f.write(f"User Consent: {result.consent_given}\n")
                f.write(f"Report Generated: {paths.summary_file}\n")
                f.write(f"Full output logged to: {paths.output_log_file}\n")


            if paths.output_log_file:
                with open(paths.output_log_file, 'w') as f:
                    f.write(result.output)

        except Exception as e:
            self.console.print(f"[bold red]Error saving report to file: {e}[/bold red]")

        status_style = "bold green" if result.success else "bold red"
        status_text = "Success" if result.success else "Failure"

        report_text = Text()
        report_text.append("Tool: ", style="bold")
        report_text.append(f"{result.command.tool_name}\n")
        report_text.append("Status: ", style="bold")
        report_text.append(status_text, style=status_style)
        report_text.append("\nReport saved: ", style="bold")
        report_text.append(str(paths.summary_file))

        panel = Panel(
            report_text,
            title="[bold blue]Execution Report[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
