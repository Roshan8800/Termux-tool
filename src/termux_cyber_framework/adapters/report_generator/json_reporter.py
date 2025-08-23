import json
import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from rich.console import Console

class JsonReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a JSON file on the filesystem.
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
        Saves the report to a JSON file.
        """
        summary_file = os.path.join(paths.run_dir, f"{paths.base_filename}.json")
        report = {
            "tool_used": result.command.tool_name,
            "command_executed": result.command.raw_command,
            "ai_interpretation": result.command.ai_interpretation,
            "execution_time": str(result.end_time - result.start_time),
            "exit_code": result.error.error_code if result.error else 0,
            "status": "Success" if result.success else "Failure",
            "error_message": result.error.message if result.error else None,
            "ai_error_analysis": result.error.ai_analysis if result.error else None,
            "ai_security_advice": result.ai_advice,
            "user_consent": result.consent_given,
            "report_generated": str(summary_file),
            "output_log_file": str(paths.output_log_file),
            "output": result.output,
        }

        report_content = json.dumps(report, indent=4)
        if not self.file_manager.write_file(summary_file, report_content):
            self.console.print(f"[bold red]Error saving JSON report to file: {summary_file}[/bold red]")

        # The TxtReporter is responsible for writing the raw output log
        # and printing to console, so this agent only handles the JSON file.
        pass
