import os
import json
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths

class JsonReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a JSON file on the filesystem.
    """
    def __init__(self, reports_dir="reports"):
        self.reports_dir = reports_dir
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")

        tool_name = tool_name.replace(" ", "_").replace("/", "")
        run_dir = os.path.join(self.reports_dir, date_str, tool_name, time_str)
        os.makedirs(run_dir, exist_ok=True)

        summary_path = os.path.join(run_dir, "summary.json")
        run_log_path = os.path.join(run_dir, "run.log")
        return RunPaths(summary_file=summary_path, output_log_file=run_log_path)

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Saves the report to a JSON file and the raw output to a log file.
        """
        try:
            # Save summary.json
            with open(paths.summary_file, 'w') as f:
                f.write(result.model_dump_json(indent=4))

            # Save run.log
            with open(paths.output_log_file, 'w') as f:
                f.write("--- STDOUT ---\n")
                f.write(result.output)
                f.write("\n\n--- STDERR ---\n")
                if result.error:
                    f.write(result.error.message)
        except Exception as e:
            print(f"Error saving report to file: {e}")

        print(f"\n--- Execution Report ---")
        print(f"[*] Command: {result.command.raw_command}")
        print(f"[*] Success: {result.success}")
        if not result.success and result.error:
            print(f"[*] Error: {result.error.message}")
        print(f"[+] Report saved to: {paths.summary_file}")
