import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.core.domain.run_paths import RunPaths

class TxtReporter(ReportGeneratorPort):
    """
    A report generator that saves the report to a text file on the filesystem.
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
        run_dir = os.path.join(self.reports_dir, date_str, tool_name)
        os.makedirs(run_dir, exist_ok=True)

        report_path = os.path.join(run_dir, f"{time_str}.txt")
        return RunPaths(summary_file=report_path, output_log_file=None)

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        """
        Saves the report to a text file.
        """
        try:
            with open(paths.summary_file, 'w') as f:
                f.write(f"Tool: {result.command.tool_name}\n")
                f.write(f"Target: {' '.join(result.command.args)}\n")
                f.write(f"Status: {'Success' if result.success else 'Failure'}\n")
                if result.error:
                    f.write(f"Error: {result.error.message}\n")
                f.write("\n--- OUTPUT ---\n")
                f.write(result.output)
        except Exception as e:
            print(f"Error saving report to file: {e}")

        print(f"\n--- Execution Report ---")
        print(f"Tool: {result.command.tool_name}")
        print(f"Target: {' '.join(result.command.args)}")
        print(f"Status: {'Success' if result.success else 'Failure'}")
        print(f"Report saved: {paths.summary_file}")
