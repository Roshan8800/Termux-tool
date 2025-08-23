import os
import json
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class TxtReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a text file on the filesystem.
    """
    def __init__(self, file_manager: FileManagerAgent, reports_dir="reports"):
        self.file_manager = file_manager
        self.reports_dir = reports_dir
        self.console = Console()
        self.file_manager.create_directory(self.reports_dir)

    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")

        tool_name = tool_name.replace(" ", "_").replace("/", "")
        run_dir = os.path.join(self.reports_dir, date_str, tool_name)
        self.file_manager.create_directory(run_dir)

        base_filename = f"{time_str}"
        log_path = os.path.join(run_dir, f"{base_filename}.log")
        return RunPaths(run_dir=run_dir, base_filename=base_filename, output_log_file=log_path)

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Saves the report to a text file and the output to a log file.
        """
        summary_file = os.path.join(paths.run_dir, f"{paths.base_filename}.txt")

        report_content = "--- Execution Report ---\n"
        report_content += f"Tool Used: {result.command.tool_name}\n"
        report_content += f"Command Executed: {result.command.raw_command}\n"
        if result.command.ai_interpretation:
            report_content += f"AI Interpretation: {json.dumps(result.command.ai_interpretation)}\n"
        report_content += f"Execution Time: {result.end_time - result.start_time}\n"
        report_content += f"Exit Code: {result.error.error_code if result.error else 0}\n"
        report_content += f"Status: {'Success' if result.success else 'Failure'}\n"
        if result.error:
            report_content += f"Error Message: {result.error.message}\n"
            if result.error.ai_analysis:
                report_content += "\n--- AI Error Analysis ---\n"
                report_content += f"{result.error.ai_analysis}\n"
        if result.ai_advice:
            report_content += "\n--- AI Security Advisor ---\n"
            report_content += f"{result.ai_advice}\n"
        report_content += f"User Consent: {result.consent_given}\n"
        report_content += f"Report Generated: {summary_file}\n"
        report_content += f"Full output logged to: {paths.output_log_file}\n"

        if not self.file_manager.write_file(summary_file, report_content):
            self.console.print(f"[bold red]Error saving text report to file: {summary_file}[/bold red]")

        if paths.output_log_file:
            if not self.file_manager.write_file(paths.output_log_file, result.output):
                self.console.print(f"[bold red]Error saving log output to file: {paths.output_log_file}[/bold red]")

        # Console output remains the same
        status_style = "bold green" if result.success else "bold red"
        status_text = "Success" if result.success else "Failure"
        report_text = Text()
        report_text.append("Tool: ", style="bold")
        report_text.append(f"{result.command.tool_name}\n")
        report_text.append("Status: ", style="bold")
        report_text.append(status_text, style=status_style)
        report_text.append("\nReport saved: ", style="bold")
        report_text.append(str(summary_file))
        panel = Panel(report_text, title="[bold blue]Execution Report[/bold blue]", border_style="blue")
        self.console.print(panel)
